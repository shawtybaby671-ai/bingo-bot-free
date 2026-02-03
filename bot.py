from flask import Flask, request, jsonify
import telebot
from telebot import types
import os
import random
import io
from PIL import Image, ImageDraw
import sqlite3
import threading
import time
from datetime import datetime
import json

app = Flask(__name__)

# Player data directory
PLAYER_DATA_DIR = 'player_data'
os.makedirs(PLAYER_DATA_DIR, exist_ok=True)

# ENV VARS (Set in Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN and os.path.exists('/etc/secrets/bot-token'):
    with open('/etc/secrets/bot-token', 'r', encoding='utf-8') as f:
        BOT_TOKEN = f.read().strip()
BOT_TOKEN = BOT_TOKEN or 'YOUR_BOT_TOKEN'

ADMIN_ID = int(os.environ.get('ADMIN_ID', '1397131889'))
bot = telebot.TeleBot(BOT_TOKEN)

# Game State - per chat/group
# Structure: {chat_id: {'active': bool, 'called_numbers': [], 'players': {}, 'jackpot': int, 'game_id': int, 'game_type': str, 'pattern': str}}
games = {}

# Global Daily Tournament State
daily_tournament = {
    'active': False,
    'called_numbers': [],
    'players': {},  # {chat_id: {user_id: {'card': card, 'card_type': str}}}
    'jackpot': 100,  # Higher jackpot for tournaments
    'game_id': 0,
    'game_type': 'classic',
    'pattern': 'single_line',
    'start_time': None,
    'participating_groups': set()
}

# Database
def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games 
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, numbers TEXT, winner TEXT, game_type TEXT, pattern TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS approved_groups
                 (chat_id INTEGER PRIMARY KEY, chat_title TEXT, approved_by INTEGER, approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_schedule
                 (id INTEGER PRIMARY KEY, schedule_time TEXT, enabled INTEGER DEFAULT 1, 
                  game_type TEXT DEFAULT 'classic', pattern TEXT DEFAULT 'blackout')''')
    c.execute('''CREATE TABLE IF NOT EXISTS tournament_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tournament_id INTEGER, chat_id INTEGER, 
                  winner_user_id INTEGER, winner_name TEXT, prize INTEGER, completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Player profile table
    c.execute('''CREATE TABLE IF NOT EXISTS player_profiles
                 (user_id INTEGER PRIMARY KEY, username TEXT, points INTEGER DEFAULT 100, 
                  cards_owned INTEGER DEFAULT 0, join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Scheduled games table
    c.execute('''CREATE TABLE IF NOT EXISTS scheduled_games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, game_date TEXT, game_time TEXT, 
                  game_type TEXT, pattern TEXT, max_players INTEGER DEFAULT 50, 
                  entry_cost INTEGER DEFAULT 10, status TEXT DEFAULT 'scheduled',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Game registrations table
    c.execute('''CREATE TABLE IF NOT EXISTS game_registrations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, game_id INTEGER, user_id INTEGER, 
                  username TEXT, cards_requested INTEGER, points_paid INTEGER, 
                  status TEXT DEFAULT 'pending', admin_approved TEXT DEFAULT 'pending',
                  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(game_id) REFERENCES scheduled_games(id))''')
    
    conn.commit()
    conn.close()
init_db()

def is_group_approved(chat_id):
    """Check if a group is approved to run games."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT chat_id FROM approved_groups WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def approve_group(chat_id, chat_title, admin_id):
    """Approve a group to run games."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO approved_groups (chat_id, chat_title, approved_by) VALUES (?, ?, ?)",
              (chat_id, chat_title, admin_id))
    conn.commit()
    conn.close()

def unapprove_group(chat_id):
    """Remove approval for a group."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("DELETE FROM approved_groups WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

def get_game_state(chat_id):
    """Get or create game state for a chat."""
    if chat_id not in games:
        games[chat_id] = {
            'active': False,
            'called_numbers': [],
            'players': {},
            'jackpot': 0,
            'game_id': 0,
            'game_type': 'classic',
            'pattern': 'single_line'
        }
    return games[chat_id]

def get_all_approved_groups():
    """Get list of all approved group chat IDs."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT chat_id, chat_title FROM approved_groups")
    groups = c.fetchall()
    conn.close()
    return groups

def schedule_daily_tournament(schedule_time, game_type='classic', pattern='blackout'):
    """Schedule a daily tournament."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("INSERT INTO daily_schedule (schedule_time, game_type, pattern) VALUES (?, ?, ?)",
              (schedule_time, game_type, pattern))
    conn.commit()
    conn.close()

def get_daily_schedule():
    """Get the daily tournament schedule."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT id, schedule_time, game_type, pattern, enabled FROM daily_schedule WHERE enabled = 1 LIMIT 1")
    schedule = c.fetchone()
    conn.close()
    return schedule

# Player Management Functions
def get_or_create_player(user_id, username):
    """Get player profile or create if doesn't exist."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, points, cards_owned FROM player_profiles WHERE user_id = ?", (user_id,))
    player = c.fetchone()
    
    if not player:
        # Create new player with starting points
        c.execute("INSERT INTO player_profiles (user_id, username, points) VALUES (?, ?, ?)",
                 (user_id, username, 100))
        conn.commit()
        player = (user_id, username, 100, 0)
    
    conn.close()
    return player

def update_player_points(user_id, points_delta):
    """Update player points (positive or negative delta)."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("UPDATE player_profiles SET points = points + ? WHERE user_id = ?", (points_delta, user_id))
    conn.commit()
    conn.close()

def get_scheduled_games():
    """Get list of scheduled games."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""SELECT id, game_date, game_time, game_type, pattern, max_players, entry_cost, status 
                 FROM scheduled_games WHERE status = 'scheduled' ORDER BY game_date, game_time""")
    games = c.fetchall()
    conn.close()
    return games

def create_scheduled_game(game_date, game_time, game_type, pattern, max_players=50, entry_cost=10):
    """Create a new scheduled game."""
    # Validate date format and ensure it's not in the past
    try:
        from datetime import datetime
        game_datetime_str = f"{game_date} {game_time}"
        game_datetime = datetime.strptime(game_datetime_str, "%Y-%m-%d %H:%M")
        
        if game_datetime < datetime.now():
            return None  # Game is in the past
    except ValueError:
        return None  # Invalid date/time format
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""INSERT INTO scheduled_games (game_date, game_time, game_type, pattern, max_players, entry_cost)
                 VALUES (?, ?, ?, ?, ?, ?)""",
             (game_date, game_time, game_type, pattern, max_players, entry_cost))
    game_id = c.lastrowid
    conn.commit()
    conn.close()
    return game_id

def register_for_game(game_id, user_id, username, cards_requested):
    """Register player for a scheduled game."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    # Calculate points required (entry cost per card)
    c.execute("SELECT entry_cost FROM scheduled_games WHERE id = ?", (game_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return None
    
    entry_cost = result[0]
    points_required = entry_cost * cards_requested
    
    # Insert registration
    c.execute("""INSERT INTO game_registrations 
                 (game_id, user_id, username, cards_requested, points_paid, status, admin_approved)
                 VALUES (?, ?, ?, ?, ?, 'pending', 'pending')""",
             (game_id, user_id, username, cards_requested, points_required))
    registration_id = c.lastrowid
    conn.commit()
    conn.close()
    return registration_id

def get_registration(registration_id):
    """Get registration details."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""SELECT r.id, r.game_id, r.user_id, r.username, r.cards_requested, r.points_paid, 
                        r.status, r.admin_approved, g.game_date, g.game_time, g.game_type, g.pattern
                 FROM game_registrations r
                 JOIN scheduled_games g ON r.game_id = g.id
                 WHERE r.id = ?""", (registration_id,))
    registration = c.fetchone()
    conn.close()
    return registration

def approve_registration(registration_id):
    """Admin approves a registration."""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    # Get registration details
    c.execute("SELECT user_id, points_paid FROM game_registrations WHERE id = ?", (registration_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False
    
    user_id, points_paid = result
    
    # Update registration status
    c.execute("UPDATE game_registrations SET admin_approved = 'approved', status = 'confirmed' WHERE id = ?",
             (registration_id,))
    
    # Deduct points from player
    c.execute("UPDATE player_profiles SET points = points - ? WHERE user_id = ?", (points_paid, user_id))
    
    conn.commit()
    conn.close()
    return True

# Player Data File Management Functions
def save_player_dm_data(user_id, registration_id, message_type, message_data):
    """Save player-admin DM messages as JSON files."""
    filename = os.path.join(PLAYER_DATA_DIR, f'player_{user_id}_reg_{registration_id}.json')
    
    # Load existing data or create new
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            'user_id': user_id,
            'registration_id': registration_id,
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
    
    # Add new message
    message_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': message_type,
        'data': message_data
    }
    data['messages'].append(message_entry)
    data['last_updated'] = datetime.now().isoformat()
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def get_player_dm_data(user_id, registration_id):
    """Retrieve player DM data from file."""
    filename = os.path.join(PLAYER_DATA_DIR, f'player_{user_id}_reg_{registration_id}.json')
    
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_player_data_files(user_id=None):
    """List all player data files, optionally filtered by user_id."""
    files = []
    if not os.path.exists(PLAYER_DATA_DIR):
        return files
    
    for filename in os.listdir(PLAYER_DATA_DIR):
        if filename.endswith('.json'):
            if user_id is None or filename.startswith(f'player_{user_id}_'):
                files.append(os.path.join(PLAYER_DATA_DIR, filename))
    
    return files

def save_player_profile_snapshot(user_id, username, registration_data):
    """Save a snapshot of player profile and registration data."""
    filename = os.path.join(PLAYER_DATA_DIR, f'player_{user_id}_profile.json')
    
    # Load existing or create new
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            'user_id': user_id,
            'username': username,
            'created_at': datetime.now().isoformat(),
            'registrations': []
        }
    
    # Add registration to history
    registration_entry = {
        'timestamp': datetime.now().isoformat(),
        'registration_id': registration_data.get('registration_id'),
        'game_id': registration_data.get('game_id'),
        'cards_requested': registration_data.get('cards_requested'),
        'points_paid': registration_data.get('points_paid'),
        'status': registration_data.get('status'),
        'game_date': registration_data.get('game_date'),
        'game_time': registration_data.get('game_time'),
        'game_type': registration_data.get('game_type'),
        'pattern': registration_data.get('pattern')
    }
    data['registrations'].append(registration_entry)
    data['last_updated'] = datetime.now().isoformat()
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

# BINGO Pattern Definitions
# Each pattern is a list of (row, col) coordinates (0-4)
PATTERNS = {
    # Lines
    "single_line": [
        # Horizontal lines
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
        [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
        [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
        [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)],
        [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        # Vertical lines
        [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
        [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)],
        [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],
        [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3)],
        [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
        # Diagonals
        [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
        [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)],
    ],
    "four_corners": [
        [(0, 0), (0, 4), (4, 0), (4, 4)],
    ],
    "blackout": [
        [(r, c) for r in range(5) for c in range(5)],
    ],
    "letter_X": [
        [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (0, 4), (1, 3), (3, 1), (4, 0)],
    ],
    "postage_stamp": [
        # Top-left corner
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        # Top-right corner
        [(0, 3), (0, 4), (1, 3), (1, 4)],
        # Bottom-left corner
        [(3, 0), (3, 1), (4, 0), (4, 1)],
        # Bottom-right corner
        [(3, 3), (3, 4), (4, 3), (4, 4)],
    ],
}

# Column ranges for BINGO
COLUMN_RANGES = {
    0: (1, 15),    # B
    1: (16, 30),   # I
    2: (31, 45),   # N
    3: (46, 60),   # G
    4: (61, 75),   # O
}

def generate_classic_card():
    """Generate a classic 5x5 bingo card with single numbers per cell."""
    card = []
    for col in range(5):
        min_num, max_num = COLUMN_RANGES[col]
        # Get 5 unique random numbers from the column's range
        numbers = random.sample(range(min_num, max_num + 1), 5)
        card.append(numbers)
    
    # Transpose to get rows instead of columns
    card = [[card[col][row] for col in range(5)] for row in range(5)]
    # Set center as free space (None)
    card[2][2] = None
    return card

def generate_dual_action_card():
    """Generate a dual action 5x5 bingo card with two numbers per cell."""
    card = []
    for col in range(5):
        min_num, max_num = COLUMN_RANGES[col]
        # Get 10 unique random numbers for this column (2 per cell)
        numbers = random.sample(range(min_num, max_num + 1), 10)
        # Create pairs
        column_cells = [(numbers[i], numbers[i+1]) for i in range(0, 10, 2)]
        card.append(column_cells)
    
    # Transpose to get rows instead of columns
    card = [[card[col][row] for col in range(5)] for row in range(5)]
    # Set center as free space (None)
    card[2][2] = None
    return card

def is_cell_marked(cell, called_numbers, card_type):
    """Check if a cell is marked based on card type."""
    if cell is None:  # Free space
        return True
    
    if card_type == "classic":
        return cell in called_numbers
    elif card_type == "dual_action":
        return cell[0] in called_numbers or cell[1] in called_numbers
    
    return False

def check_pattern(card, marked_cells, pattern_list):
    """Check if any pattern in the list is complete."""
    for pattern in pattern_list:
        if all((r, c) in marked_cells for r, c in pattern):
            return True
    return False

def get_marked_cells(card, called_numbers, card_type):
    """Get set of marked cell coordinates."""
    marked = set()
    for r in range(5):
        for c in range(5):
            if is_cell_marked(card[r][c], called_numbers, card_type):
                marked.add((r, c))
    return marked

def format_card(card, card_type, marked_cells=None):
    """Format a bingo card as text."""
    if marked_cells is None:
        marked_cells = set()
    
    text = "```\n  B    I    N    G    O\n"
    for r in range(5):
        row_text = ""
        for c in range(5):
            cell = card[r][c]
            if cell is None:
                cell_str = "FREE"
            elif card_type == "classic":
                cell_str = f"{cell:2d}"
            else:  # dual_action
                cell_str = f"{cell[0]}/{cell[1]}"
            
            # Mark if in marked_cells
            if (r, c) in marked_cells:
                cell_str = f"[{cell_str}]"
            else:
                cell_str = f" {cell_str} "
            
            row_text += cell_str.ljust(5)
        text += row_text + "\n"
    text += "```"
    return text

def get_bingo_letter(num):
    """Get the BINGO letter for a number."""
    if 1 <= num <= 15:
        return 'B'
    elif 16 <= num <= 30:
        return 'I'
    elif 31 <= num <= 45:
        return 'N'
    elif 46 <= num <= 60:
        return 'G'
    elif 61 <= num <= 75:
        return 'O'
    return '?'

# Simple flashboard
def create_board(called):
    img = Image.new('RGB', (400, 300), color='black')
    draw = ImageDraw.Draw(img)
    
    for i in range(1, 76):
        x = (i-1) % 15 * 25 + 10
        y = (i-1) // 15 * 18 + 10
        color = 'red' if i in called else 'white'
        draw.ellipse([x, y, x+15, y+15], fill=color)
        draw.text((x+2, y+2), str(i), fill='black')
    
    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start', 'menu'])
def start_menu(message):
    """Display welcome message and main menu with inline buttons."""
    user_id = message.from_user.id
    username = message.from_user.first_name or message.from_user.username or "Player"
    
    # Ensure player profile exists
    get_or_create_player(user_id, username)
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_profile = types.InlineKeyboardButton("👤 Player Profile", callback_data="menu_profile")
    btn_commands = types.InlineKeyboardButton("📋 Commands", callback_data="menu_commands")
    btn_rules = types.InlineKeyboardButton("📖 Rules", callback_data="menu_rules")
    btn_request = types.InlineKeyboardButton("🎮 Request Game Type", callback_data="menu_request_game")
    btn_schedule = types.InlineKeyboardButton("📅 Game Schedule", callback_data="menu_schedule")
    btn_join = types.InlineKeyboardButton("🎯 Join a Game", callback_data="menu_join_game")
    
    markup.add(btn_profile, btn_commands)
    markup.add(btn_rules, btn_request)
    markup.add(btn_schedule, btn_join)
    
    welcome_text = f"🎰 *Welcome to Bingo Bot, {username}!*\n\n"
    welcome_text += "Choose an option from the menu below:"
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['commands'])
def show_commands(message):
    """Show commands list."""
    commands_text = "📋 *Available Commands:*\n\n"
    commands_text += "/start - Show main menu\n"
    commands_text += "/menu - Show main menu\n"
    commands_text += "/commands - Show this commands list\n"
    commands_text += "/profile - View your profile\n"
    commands_text += "/schedule - View game schedule\n"
    commands_text += "/mycard - View your current card\n"
    commands_text += "/status - Check group game status\n\n"
    
    if message.from_user.id == ADMIN_ID:
        commands_text += "*Admin Commands:*\n"
        commands_text += "/schedulegame - Schedule a new game\n"
        commands_text += "/approvegroup - Approve this group\n"
        commands_text += "/listgroups - List approved groups\n"
    
    bot.reply_to(message, commands_text, parse_mode='Markdown')

# Callback query handlers for inline buttons
@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_menu_callback(call):
    """Handle menu button callbacks."""
    user_id = call.from_user.id
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    if call.data == "menu_profile":
        show_player_profile(call)
    elif call.data == "menu_commands":
        show_commands_menu(call)
    elif call.data == "menu_rules":
        show_rules_menu(call)
    elif call.data == "menu_request_game":
        show_request_game_menu(call)
    elif call.data == "menu_schedule":
        show_schedule_menu(call)
    elif call.data == "menu_join_game":
        show_join_game_menu(call)
    elif call.data == "back_to_main":
        back_to_main_menu(call)

def show_player_profile(call):
    """Display player profile."""
    user_id = call.from_user.id
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    player = get_or_create_player(user_id, username)
    user_id, username, points, cards_owned = player
    
    profile_text = f"👤 *Player Profile*\n\n"
    profile_text += f"🎭 Name: {username}\n"
    profile_text += f"💎 Points: {points}\n"
    profile_text += f"🎴 Cards Owned: {cards_owned}\n"
    profile_text += f"🆔 ID: {user_id}\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(profile_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_commands_menu(call):
    """Display commands list."""
    commands_text = "📋 *Available Commands:*\n\n"
    commands_text += "• /start - Show main menu\n"
    commands_text += "• /menu - Show main menu\n"
    commands_text += "• /command - Commands list\n"
    commands_text += "• /profile - Your profile\n"
    commands_text += "• /schedule - Game schedule\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(commands_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_rules_menu(call):
    """Display game rules."""
    rules_text = "📖 *Bingo Game Rules*\n\n"
    rules_text += "*How to Play:*\n"
    rules_text += "1. Join a scheduled game from the Game Schedule menu\n"
    rules_text += "2. Select number of cards you want (costs points per card)\n"
    rules_text += "3. Approve your purchase and DM the bot\n"
    rules_text += "4. Admin will approve your request\n"
    rules_text += "5. You'll be added to the game and receive your cards\n\n"
    
    rules_text += "*Card Types:*\n"
    rules_text += "• *Classic*: Single number per cell\n"
    rules_text += "• *Dual Action*: Two numbers per cell\n\n"
    
    rules_text += "*Winning Patterns:*\n"
    rules_text += "• Single Line\n"
    rules_text += "• Four Corners\n"
    rules_text += "• Blackout (Full Card)\n"
    rules_text += "• Letter X\n"
    rules_text += "• Postage Stamp\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(rules_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_request_game_menu(call):
    """Display game type request menu."""
    request_text = "🎮 *Request Game Type*\n\n"
    request_text += "Select the type of game you'd like to request:\n"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_classic = types.InlineKeyboardButton("Classic", callback_data="request_classic")
    btn_dual = types.InlineKeyboardButton("Dual Action", callback_data="request_dual")
    btn_back = types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")
    
    markup.add(btn_classic, btn_dual)
    markup.add(btn_back)
    
    bot.edit_message_text(request_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_schedule_menu(call):
    """Display scheduled games."""
    games = get_scheduled_games()
    
    if not games:
        schedule_text = "📅 *Game Schedule*\n\n"
        schedule_text += "No games scheduled at the moment.\n"
        schedule_text += "Check back later!"
    else:
        schedule_text = "📅 *Upcoming Games*\n\n"
        for game in games:
            game_id, game_date, game_time, game_type, pattern, max_players, entry_cost, status = game
            schedule_text += f"*Game #{game_id}*\n"
            schedule_text += f"📆 Date: {game_date}\n"
            schedule_text += f"🕐 Time: {game_time}\n"
            schedule_text += f"🎮 Type: {game_type}\n"
            schedule_text += f"🏆 Pattern: {pattern}\n"
            schedule_text += f"💎 Entry: {entry_cost} points per card\n"
            schedule_text += f"👥 Max Players: {max_players}\n"
            schedule_text += "─────────────\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(schedule_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_join_game_menu(call):
    """Display games available to join."""
    games = get_scheduled_games()
    
    if not games:
        join_text = "🎯 *Join a Game*\n\n"
        join_text += "No games available to join at the moment.\n"
        join_text += "Check the schedule later!"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    else:
        join_text = "🎯 *Select a Game to Join*\n\n"
        join_text += "Click on a game to join:"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for game in games[:5]:  # Show max 5 games
            game_id, game_date, game_time, game_type, pattern, max_players, entry_cost, status = game
            btn_text = f"Game #{game_id} - {game_date} {game_time}"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"join_game_{game_id}"))
        
        markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(join_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def back_to_main_menu(call):
    """Return to main menu."""
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_profile = types.InlineKeyboardButton("👤 Player Profile", callback_data="menu_profile")
    btn_commands = types.InlineKeyboardButton("📋 Commands", callback_data="menu_commands")
    btn_rules = types.InlineKeyboardButton("📖 Rules", callback_data="menu_rules")
    btn_request = types.InlineKeyboardButton("🎮 Request Game Type", callback_data="menu_request_game")
    btn_schedule = types.InlineKeyboardButton("📅 Game Schedule", callback_data="menu_schedule")
    btn_join = types.InlineKeyboardButton("🎯 Join a Game", callback_data="menu_join_game")
    
    markup.add(btn_profile, btn_commands)
    markup.add(btn_rules, btn_request)
    markup.add(btn_schedule, btn_join)
    
    welcome_text = f"🎰 *Welcome to Bingo Bot, {username}!*\n\n"
    welcome_text += "Choose an option from the menu below:"
    
    bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# Join game workflow handlers
@bot.callback_query_handler(func=lambda call: call.data.startswith('join_game_'))
def handle_join_game(call):
    """Handle joining a specific game."""
    game_id = int(call.data.split('_')[2])
    user_id = call.from_user.id
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    # Get game details
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""SELECT id, game_date, game_time, game_type, pattern, entry_cost 
                 FROM scheduled_games WHERE id = ?""", (game_id,))
    game = c.fetchone()
    conn.close()
    
    if not game:
        bot.answer_callback_query(call.id, "Game not found!", show_alert=True)
        return
    
    game_id, game_date, game_time, game_type, pattern, entry_cost = game
    
    join_text = f"🎯 *Joining Game #{game_id}*\n\n"
    join_text += f"📆 Date: {game_date}\n"
    join_text += f"🕐 Time: {game_time}\n"
    join_text += f"🎮 Type: {game_type}\n"
    join_text += f"🏆 Pattern: {pattern}\n"
    join_text += f"💎 Cost: {entry_cost} points per card\n\n"
    join_text += "How many cards would you like?"
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(1, 7):  # 1-6 cards
        card_label = f"{i} Card" if i == 1 else f"{i} Cards"
        markup.add(types.InlineKeyboardButton(card_label, callback_data=f"cards_{game_id}_{i}"))
    markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="menu_join_game"))
    
    bot.edit_message_text(join_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cards_'))
def handle_card_selection(call):
    """Handle card count selection."""
    parts = call.data.split('_')
    game_id = int(parts[1])
    cards_requested = int(parts[2])
    user_id = call.from_user.id
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    # Get player points
    player = get_or_create_player(user_id, username)
    user_id, username, points, cards_owned = player
    
    # Get game details
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT entry_cost FROM scheduled_games WHERE id = ?", (game_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        bot.answer_callback_query(call.id, "Game not found!", show_alert=True)
        return
    
    entry_cost = result[0]
    total_cost = entry_cost * cards_requested
    
    confirm_text = f"🎴 *Confirm Purchase*\n\n"
    confirm_text += f"Cards Requested: {cards_requested}\n"
    confirm_text += f"Points Required: {total_cost}\n"
    confirm_text += f"Your Points: {points}\n\n"
    
    if total_cost > points:
        confirm_text += "❌ *Insufficient Points!*\n"
        confirm_text += f"You need {total_cost - points} more points."
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data=f"join_game_{game_id}"))
    else:
        confirm_text += "✅ You have enough points!\n\n"
        confirm_text += "Do you want to proceed?"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{game_id}_{cards_requested}"),
            types.InlineKeyboardButton("❌ Cancel", callback_data=f"join_game_{game_id}")
        )
    
    bot.edit_message_text(confirm_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def handle_approve_purchase(call):
    """Handle purchase approval."""
    parts = call.data.split('_')
    game_id = int(parts[1])
    cards_requested = int(parts[2])
    user_id = call.from_user.id
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    # Create registration
    registration_id = register_for_game(game_id, user_id, username, cards_requested)
    
    if not registration_id:
        bot.answer_callback_query(call.id, "Error creating registration!", show_alert=True)
        return
    
    # Instruction to DM bot
    dm_text = f"✅ *Request Submitted!*\n\n"
    dm_text += f"Registration ID: #{registration_id}\n"
    dm_text += f"Game ID: #{game_id}\n"
    dm_text += f"Cards: {cards_requested}\n\n"
    dm_text += "📩 *Next Steps:*\n"
    dm_text += "1. Click the button below to start a DM with the bot\n"
    dm_text += "2. Click 'Start' in the DM\n"
    dm_text += "3. Wait for admin approval\n"
    dm_text += "4. Once approved, your points will be deducted and you'll be added to the game!"
    
    markup = types.InlineKeyboardMarkup()
    bot_username = bot.get_me().username
    dm_url = f"https://t.me/{bot_username}?start=reg_{registration_id}"
    markup.add(types.InlineKeyboardButton("💬 Open DM with Bot", url=dm_url))
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(dm_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id, "Request submitted! Please DM the bot.")

# Handle DM start with registration parameter
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/start reg_'))
def handle_dm_registration_start(message):
    """Handle when player DMs bot with registration link."""
    try:
        registration_id = int(message.text.split('_')[1])
    except:
        bot.reply_to(message, "Invalid registration link!")
        return
    
    user_id = message.from_user.id
    username = message.from_user.first_name or message.from_user.username or "Player"
    
    # Get registration details
    registration = get_registration(registration_id)
    
    if not registration:
        bot.reply_to(message, "❌ Registration not found!")
        return
    
    (reg_id, game_id, reg_user_id, reg_username, cards_requested, points_paid, 
     status, admin_approved, game_date, game_time, game_type, pattern) = registration
    
    if reg_user_id != user_id:
        bot.reply_to(message, "❌ This registration doesn't belong to you!")
        return
    
    if admin_approved != 'pending':
        bot.reply_to(message, f"ℹ️ This registration is already {admin_approved}.")
        return
    
    # Send admin approval request
    admin_text = f"🔔 *New Registration Request*\n\n"
    admin_text += f"👤 Player: {reg_username} (ID: {reg_user_id})\n"
    admin_text += f"🎮 Game #{game_id}\n"
    admin_text += f"📆 {game_date} {game_time}\n"
    admin_text += f"🎴 Cards: {cards_requested}\n"
    admin_text += f"💎 Points: {points_paid}\n"
    admin_text += f"🏆 Type: {game_type} - {pattern}\n\n"
    admin_text += "Do you approve this registration?"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{registration_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{registration_id}")
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode='Markdown')
        
        # Confirm to player
        confirm_text = f"✅ *Request Sent to Admin!*\n\n"
        confirm_text += f"Registration ID: #{registration_id}\n"
        confirm_text += f"Game: #{game_id} on {game_date}\n"
        confirm_text += f"Cards: {cards_requested}\n\n"
        confirm_text += "⏳ Please wait for admin approval.\n"
        confirm_text += "You'll be notified once the decision is made."
        
        bot.reply_to(message, confirm_text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Error sending approval request: {str(e)}")

# Admin approval handlers
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_approve_'))
def handle_admin_approve(call):
    """Admin approves a registration."""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Only admin can approve!", show_alert=True)
        return
    
    registration_id = int(call.data.split('_')[2])
    
    # Get registration details before approval
    registration = get_registration(registration_id)
    if not registration:
        bot.answer_callback_query(call.id, "Registration not found!", show_alert=True)
        return
    
    (reg_id, game_id, user_id, username, cards_requested, points_paid, 
     status, admin_approved, game_date, game_time, game_type, pattern) = registration
    
    # Approve registration
    success = approve_registration(registration_id)
    
    if success:
        # Update admin message
        approved_text = call.message.text + "\n\n✅ *APPROVED*"
        bot.edit_message_text(approved_text, call.message.chat.id, call.message.message_id, 
                             parse_mode='Markdown')
        
        # Notify player
        notify_text = f"🎉 *Registration Approved!*\n\n"
        notify_text += f"Game #{game_id} on {game_date}\n"
        notify_text += f"Cards: {cards_requested}\n"
        notify_text += f"Points Deducted: {points_paid}\n\n"
        notify_text += "You've been added to the card holder list!\n"
        notify_text += "You'll receive your cards when the game starts."
        
        try:
            bot.send_message(user_id, notify_text, parse_mode='Markdown')
        except:
            pass
        
        bot.answer_callback_query(call.id, "Registration approved!")
    else:
        bot.answer_callback_query(call.id, "Error approving registration!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_reject_'))
def handle_admin_reject(call):
    """Admin rejects a registration."""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Only admin can reject!", show_alert=True)
        return
    
    registration_id = int(call.data.split('_')[2])
    
    # Get registration details
    registration = get_registration(registration_id)
    if not registration:
        bot.answer_callback_query(call.id, "Registration not found!", show_alert=True)
        return
    
    (reg_id, game_id, user_id, username, cards_requested, points_paid, 
     status, admin_approved, game_date, game_time, game_type, pattern) = registration
    
    # Update registration status
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("UPDATE game_registrations SET admin_approved = 'rejected', status = 'rejected' WHERE id = ?",
             (registration_id,))
    conn.commit()
    conn.close()
    
    # Update admin message
    rejected_text = call.message.text + "\n\n❌ *REJECTED*"
    bot.edit_message_text(rejected_text, call.message.chat.id, call.message.message_id, 
                         parse_mode='Markdown')
    
    # Notify player
    notify_text = f"❌ *Registration Rejected*\n\n"
    notify_text += f"Game #{game_id} on {game_date}\n"
    notify_text += f"Your registration was not approved.\n\n"
    notify_text += "No points were deducted.\n"
    notify_text += "You can try joining another game."
    
    try:
        bot.send_message(user_id, notify_text, parse_mode='Markdown')
    except:
        pass
    
    bot.answer_callback_query(call.id, "Registration rejected!")

# Request game type handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('request_'))
def handle_request_game_type(call):
    """Handle game type request."""
    game_type = call.data.split('_')[1]
    user_id = call.from_user.id
    username = call.from_user.first_name or call.from_user.username or "Player"
    
    request_text = f"✅ *Request Sent!*\n\n"
    request_text += f"You've requested a *{game_type}* game.\n"
    request_text += "The admin has been notified."
    
    # Notify admin
    admin_msg = f"🎮 *Game Type Request*\n\n"
    admin_msg += f"From: {username} (ID: {user_id})\n"
    admin_msg += f"Requested: {game_type} game"
    
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
    except:
        pass
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main"))
    
    bot.edit_message_text(request_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['approvegroup'])
def approve_group_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
    
    chat_id = message.chat.id
    chat_title = message.chat.title or "Private Chat"
    
    if is_group_approved(chat_id):
        bot.reply_to(message, f"✅ Group '{chat_title}' is already approved!")
        return
    
    approve_group(chat_id, chat_title, ADMIN_ID)
    bot.reply_to(message, f"✅ Group '{chat_title}' has been approved for bingo games!")

@bot.message_handler(commands=['unapprovegroup'])
def unapprove_group_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
    
    chat_id = message.chat.id
    chat_title = message.chat.title or "Private Chat"
    
    if not is_group_approved(chat_id):
        bot.reply_to(message, f"❌ Group '{chat_title}' is not approved!")
        return
    
    unapprove_group(chat_id)
    bot.reply_to(message, f"✅ Group '{chat_title}' approval has been removed!")

@bot.message_handler(commands=['listgroups'])
def list_groups_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT chat_id, chat_title, approved_at FROM approved_groups")
    groups = c.fetchall()
    conn.close()
    
    if not groups:
        bot.reply_to(message, "📋 No approved groups yet.")
        return
    
    text = "📋 *Approved Groups:*\n\n"
    for chat_id, title, approved_at in groups:
        text += f"• {title} (ID: {chat_id})\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['schedulegame'])
def schedule_game_cmd(message):
    """Admin command to schedule a new game."""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
    
    # Parse command: /schedulegame <date> <time> <type> <pattern> [entry_cost]
    # Example: /schedulegame 2026-02-10 18:00 classic single_line 10
    parts = message.text.split()
    
    if len(parts) < 5:
        help_text = "📅 *Schedule a Game*\n\n"
        help_text += "*Usage:*\n"
        help_text += "`/schedulegame <date> <time> <type> <pattern> [cost]`\n\n"
        help_text += "*Example:*\n"
        help_text += "`/schedulegame 2026-02-10 18:00 classic single_line 10`\n\n"
        help_text += "*Types:* classic, dual_action\n"
        help_text += "*Patterns:* single_line, four_corners, blackout, letter_X, postage_stamp"
        bot.reply_to(message, help_text, parse_mode='Markdown')
        return
    
    try:
        game_date = parts[1]
        game_time = parts[2]
        game_type = parts[3]
        pattern = parts[4]
        entry_cost = 10  # Default
        
        # Parse entry cost with validation
        if len(parts) > 5:
            try:
                entry_cost = int(parts[5])
                if entry_cost < 1 or entry_cost > 1000:
                    bot.reply_to(message, "❌ Entry cost must be between 1 and 1000 points.")
                    return
            except ValueError:
                bot.reply_to(message, "❌ Entry cost must be a valid number.")
                return
        
        # Validate game type and pattern
        valid_types = ['classic', 'dual_action']
        valid_patterns = ['single_line', 'four_corners', 'blackout', 'letter_X', 'postage_stamp']
        
        if game_type not in valid_types:
            bot.reply_to(message, f"❌ Invalid game type. Use: {', '.join(valid_types)}")
            return
        
        if pattern not in valid_patterns:
            bot.reply_to(message, f"❌ Invalid pattern. Use: {', '.join(valid_patterns)}")
            return
        
        # Create scheduled game (will validate date/time)
        game_id = create_scheduled_game(game_date, game_time, game_type, pattern, entry_cost=entry_cost)
        
        if not game_id:
            bot.reply_to(message, "❌ Invalid date/time format or game is scheduled in the past.\nUse format: YYYY-MM-DD HH:MM (24-hour)")
            return
        
        success_text = f"✅ *Game Scheduled!*\n\n"
        success_text += f"Game ID: #{game_id}\n"
        success_text += f"📆 Date: {game_date}\n"
        success_text += f"🕐 Time: {game_time}\n"
        success_text += f"🎮 Type: {game_type}\n"
        success_text += f"🏆 Pattern: {pattern}\n"
        success_text += f"💎 Entry Cost: {entry_cost} points per card\n\n"
        success_text += "Players can now join this game from the menu!"
        
        bot.reply_to(message, success_text, parse_mode='Markdown')
        
    except IndexError:
        bot.reply_to(message, "❌ Missing required parameters. Use /schedulegame for help.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error scheduling game: {str(e)}")

@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    """Show player profile."""
    user_id = message.from_user.id
    username = message.from_user.first_name or message.from_user.username or "Player"
    
    player = get_or_create_player(user_id, username)
    user_id, username, points, cards_owned = player
    
    profile_text = f"👤 *Your Profile*\n\n"
    profile_text += f"🎭 Name: {username}\n"
    profile_text += f"💎 Points: {points}\n"
    profile_text += f"🎴 Cards Owned: {cards_owned}\n"
    profile_text += f"🆔 ID: {user_id}\n"
    
    bot.reply_to(message, profile_text, parse_mode='Markdown')

@bot.message_handler(commands=['schedule'])
def schedule_cmd(message):
    """Show game schedule."""
    games = get_scheduled_games()
    
    if not games:
        bot.reply_to(message, "📅 No games scheduled at the moment.")
        return
    
    schedule_text = "📅 *Upcoming Games*\n\n"
    for game in games:
        game_id, game_date, game_time, game_type, pattern, max_players, entry_cost, status = game
        schedule_text += f"*Game #{game_id}*\n"
        schedule_text += f"📆 {game_date} at {game_time}\n"
        schedule_text += f"🎮 {game_type} - {pattern}\n"
        schedule_text += f"💎 {entry_cost} points/card\n"
        schedule_text += "─────────────\n"
    
    bot.reply_to(message, schedule_text, parse_mode='Markdown')

@bot.message_handler(commands=['starttournament'])
def start_tournament_cmd(message):
    """Start a multi-group daily tournament."""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
    
    if daily_tournament['active']:
        bot.reply_to(message, "⚠️ A tournament is already active!")
        return
    
    # Parse arguments for game type and pattern
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if len(args) >= 1 and args[0] in ["classic", "dual_action"]:
        daily_tournament['game_type'] = args[0]
    else:
        daily_tournament['game_type'] = "classic"
    
    if len(args) >= 2 and args[1] in PATTERNS:
        daily_tournament['pattern'] = args[1]
    else:
        daily_tournament['pattern'] = "blackout"
    
    # Initialize tournament
    daily_tournament['active'] = True
    daily_tournament['called_numbers'] = []
    daily_tournament['players'] = {}
    daily_tournament['game_id'] += 1
    daily_tournament['jackpot'] = 100 + (daily_tournament['game_id'] * 10)
    daily_tournament['start_time'] = time.time()
    daily_tournament['participating_groups'] = set()
    
    # Broadcast to all approved groups
    groups = get_all_approved_groups()
    
    tournament_msg = f"🏆 *DAILY TOURNAMENT #{daily_tournament['game_id']}*\n\n"
    tournament_msg += f"🎯 Type: {daily_tournament['game_type']}\n"
    tournament_msg += f"🏅 Pattern: {daily_tournament['pattern'].replace('_', ' ').title()}\n"
    tournament_msg += f"💰 Jackpot: ${daily_tournament['jackpot']}\n"
    tournament_msg += f"🌐 Multi-Group Competition\n\n"
    tournament_msg += "Use /jointournament to participate!"
    
    for chat_id, title in groups:
        try:
            bot.send_message(chat_id, tournament_msg, parse_mode='Markdown')
        except Exception as e:
            print(f"Failed to send to {title}: {e}")
    
    # Start the game loop
    threading.Thread(target=tournament_game_loop).start()
    
    bot.reply_to(message, f"✅ Tournament started! Broadcasting to {len(groups)} groups.")

@bot.message_handler(commands=['jointournament'])
def join_tournament_cmd(message):
    """Join the daily tournament and get a card."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if not daily_tournament['active']:
        bot.reply_to(message, "❌ No active tournament. Wait for the daily tournament to start!")
        return
    
    if not is_group_approved(chat_id):
        bot.reply_to(message, "❌ This group is not approved for tournaments!")
        return
    
    # Initialize chat in players dict if needed
    if chat_id not in daily_tournament['players']:
        daily_tournament['players'][chat_id] = {}
        daily_tournament['participating_groups'].add(chat_id)
    
    if user_id in daily_tournament['players'][chat_id]:
        bot.reply_to(message, "✅ You already joined! Use /tournamentcard to view your card.")
        return
    
    # Generate card
    if daily_tournament['game_type'] == "classic":
        card = generate_classic_card()
    else:
        card = generate_dual_action_card()
    
    daily_tournament['players'][chat_id][user_id] = {
        'card': card,
        'card_type': daily_tournament['game_type'],
        'username': message.from_user.first_name or message.from_user.username or "Player"
    }
    
    marked = get_marked_cells(card, daily_tournament['called_numbers'], daily_tournament['game_type'])
    card_text = format_card(card, daily_tournament['game_type'], marked)
    
    response = f"🏆 *Tournament Card* (Game #{daily_tournament['game_id']})\n"
    response += f"Type: {daily_tournament['game_type']}\n\n"
    response += card_text
    response += f"\n\nPattern: {daily_tournament['pattern'].replace('_', ' ').title()}"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['tournamentcard'])
def tournament_card_cmd(message):
    """View your tournament card."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if not daily_tournament['active']:
        bot.reply_to(message, "❌ No active tournament.")
        return
    
    if chat_id not in daily_tournament['players'] or user_id not in daily_tournament['players'][chat_id]:
        bot.reply_to(message, "❌ You haven't joined the tournament! Use /jointournament.")
        return
    
    player = daily_tournament['players'][chat_id][user_id]
    card = player['card']
    card_type = player['card_type']
    
    marked = get_marked_cells(card, daily_tournament['called_numbers'], card_type)
    card_text = format_card(card, card_type, marked)
    
    response = f"🏆 *Your Tournament Card* (Game #{daily_tournament['game_id']})\n\n"
    response += card_text
    response += f"\n\n📊 Marked: {len(marked)}/25"
    
    # Check if player has winning pattern
    if daily_tournament['active'] and check_pattern(card, marked, PATTERNS[daily_tournament['pattern']]):
        response += "\n\n🎉 *YOU HAVE A WINNING PATTERN!* Type 'TOURNAMENT BINGO' to claim!"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['tournamentstatus'])
def tournament_status_cmd(message):
    """Check tournament status."""
    if not daily_tournament['active']:
        status_text = "❌ *No Active Tournament*\n\n"
        if daily_tournament['game_id'] > 0:
            status_text += f"📊 Last Tournament: #{daily_tournament['game_id']}\n"
        status_text += f"💰 Next Jackpot: ${daily_tournament['jackpot']}\n"
        bot.reply_to(message, status_text, parse_mode='Markdown')
        return
    
    # Count total players
    total_players = sum(len(players) for players in daily_tournament['players'].values())
    
    last_number = daily_tournament['called_numbers'][-1] if daily_tournament['called_numbers'] else None
    progress_percentage = int((len(daily_tournament['called_numbers']) / 75) * 100)
    filled = int(progress_percentage / 10)
    progress_bar = "█" * filled + "░" * (10 - filled)
    
    status_text = f"🏆 *TOURNAMENT #{daily_tournament['game_id']} ACTIVE*\n\n"
    status_text += f"🎲 Type: {daily_tournament['game_type']}\n"
    status_text += f"🏅 Pattern: {daily_tournament['pattern'].replace('_', ' ').title()}\n"
    status_text += f"📊 Called: {len(daily_tournament['called_numbers'])}/75\n"
    status_text += f"📈 Progress: {progress_bar} {progress_percentage}%\n\n"
    
    if last_number:
        letter = get_bingo_letter(last_number)
        status_text += f"🎱 Last Called: *{letter}-{last_number}*\n"
    
    status_text += f"💰 Jackpot: *${daily_tournament['jackpot']}*\n"
    status_text += f"🌐 Groups: {len(daily_tournament['participating_groups'])}\n"
    status_text += f"👥 Total Players: {total_players}\n"
    
    # Show recent numbers
    if len(daily_tournament['called_numbers']) >= 5:
        recent = daily_tournament['called_numbers'][-5:]
        recent_with_letters = [f"{get_bingo_letter(n)}-{n}" for n in recent]
        status_text += f"\n🔢 Recent: {', '.join(recent_with_letters)}"
    
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['startgame'])
def start_game(message):
    chat_id = message.chat.id
    
    # Check if admin
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
    
    # Check if group is approved
    if not is_group_approved(chat_id):
        bot.reply_to(message, "❌ This group is not approved for bingo games!\nUse /approvegroup to approve it.")
        return
    
    game = get_game_state(chat_id)
    
    if game['active']:
        bot.reply_to(message, "⚠️ A game is already active in this group!")
        return
    
    # Reset game state
    game['active'] = True
    game['called_numbers'] = []
    game['players'] = {}
    game['game_id'] += 1
    game['jackpot'] += 10
    
    # Parse arguments for game type and pattern (optional)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if len(args) >= 1 and args[0] in ["classic", "dual_action"]:
        game['game_type'] = args[0]
    else:
        game['game_type'] = "classic"
    
    if len(args) >= 2 and args[1] in PATTERNS:
        game['pattern'] = args[1]
    else:
        game['pattern'] = "single_line"
    
    game_info = f"🎮 *GAME #{game['game_id']} STARTED*\n"
    game_info += f"🎯 Type: {game['game_type']}\n"
    game_info += f"🏆 Pattern: {game['pattern'].replace('_', ' ').title()}\n"
    game_info += f"💰 Jackpot: ${game['jackpot']}\n\n"
    game_info += "Use /getcard to get your bingo card!"
    
    bot.send_message(chat_id, game_info, parse_mode='Markdown')
    threading.Thread(target=game_loop, args=(chat_id,)).start()

@bot.message_handler(commands=['getcard'])
def get_card(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    game = get_game_state(chat_id)
    
    if not game['active']:
        bot.reply_to(message, "❌ No active game. Wait for admin to start a game!")
        return
    
    if user_id in game['players']:
        bot.reply_to(message, "✅ You already have a card! Use /mycard to view it.")
        return
    
    # Generate card based on current game type
    if game['game_type'] == "classic":
        card = generate_classic_card()
    else:
        card = generate_dual_action_card()
    
    game['players'][user_id] = {
        'card': card,
        'card_type': game['game_type']
    }
    
    marked = get_marked_cells(card, game['called_numbers'], game['game_type'])
    card_text = format_card(card, game['game_type'], marked)
    
    response = f"🎰 *Your Bingo Card* (Game #{game['game_id']})\n"
    response += f"Type: {game['game_type']}\n\n"
    response += card_text
    response += f"\n\nPattern to win: {game['pattern'].replace('_', ' ').title()}"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['mycard'])
def my_card(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    game = get_game_state(chat_id)
    
    if user_id not in game['players']:
        bot.reply_to(message, "❌ You don't have a card yet! Use /getcard to get one.")
        return
    
    player = game['players'][user_id]
    card = player['card']
    card_type = player['card_type']
    
    marked = get_marked_cells(card, game['called_numbers'], card_type)
    card_text = format_card(card, card_type, marked)
    
    response = f"🎰 *Your Bingo Card* (Game #{game['game_id']})\n\n"
    response += card_text
    response += f"\n\n📊 Marked: {len(marked)}/25"
    
    # Check if player has winning pattern
    if game['active'] and check_pattern(card, marked, PATTERNS[game['pattern']]):
        response += "\n\n🎉 *YOU HAVE A WINNING PATTERN!* Type 'BINGO' to claim!"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status(message):
    chat_id = message.chat.id
    game = get_game_state(chat_id)
    
    if not game['active']:
        # Show information even when no game is active
        status_text = "❌ *No Active Game*\n\n"
        if game['game_id'] > 0:
            status_text += f"📊 Last Game: #{game['game_id']}\n"
        status_text += f"💰 Current Jackpot: ${game['jackpot']}\n"
        
        if is_group_approved(chat_id):
            status_text += "\n✅ This group is approved for games!"
        else:
            status_text += "\n❌ This group is not approved for games."
        
        bot.reply_to(message, status_text, parse_mode='Markdown')
        return
    
    # Enhanced status for active game
    last_number = game['called_numbers'][-1] if game['called_numbers'] else None
    progress_percentage = int((len(game['called_numbers']) / 75) * 100)
    
    # Create progress bar
    filled = int(progress_percentage / 10)
    progress_bar = "█" * filled + "░" * (10 - filled)
    
    status_text = f"🎯 *GAME #{game['game_id']} ACTIVE*\n\n"
    status_text += f"🎲 Type: {game['game_type']}\n"
    status_text += f"🏆 Pattern: {game['pattern'].replace('_', ' ').title()}\n"
    status_text += f"📊 Called Numbers: {len(game['called_numbers'])}/75\n"
    status_text += f"📈 Progress: {progress_bar} {progress_percentage}%\n\n"
    
    if last_number:
        letter = get_bingo_letter(last_number)
        status_text += f"🎱 Last Called: *{letter}-{last_number}*\n"
    
    status_text += f"💰 Jackpot: *${game['jackpot']}*\n"
    
    # Show player count if available
    if game['players']:
        status_text += f"👥 Players: {len(game['players'])}\n"
    
    # Show recent numbers (last 5)
    if len(game['called_numbers']) >= 5:
        recent = game['called_numbers'][-5:]
        recent_with_letters = [f"{get_bingo_letter(n)}-{n}" for n in recent]
        status_text += f"\n🔢 Recent: {', '.join(recent_with_letters)}"
    
    bot.reply_to(message, status_text, parse_mode='Markdown')

def game_loop(chat_id):
    game = get_game_state(chat_id)
    
    while game['active'] and len(game['called_numbers']) < 75:
        num = random.randint(1, 75)
        if num not in game['called_numbers']:
            game['called_numbers'].append(num)
            
            # Send board + number with proper BINGO letter
            letter = get_bingo_letter(num)
            board = create_board(game['called_numbers'])
            bot.send_photo(chat_id, board, caption=f"🎱 *{letter}-{num}* Called ({len(game['called_numbers'])}/75)")
            
            # Check for winners after each call
            check_for_winners(chat_id)
            
            # Jackpot boost every 10 numbers
            if len(game['called_numbers']) % 10 == 0:
                bot.send_message(chat_id, f"🔥 *HOT NUMBERS!*\nJackpot now ${game['jackpot'] + 5}")
                game['jackpot'] += 5
            
            time.sleep(3)
    
    game['active'] = False
    bot.send_message(chat_id, "🏁 *GAME OVER*\nNew game soon!")

def check_for_winners(chat_id):
    """Check if any player has achieved the winning pattern."""
    game = get_game_state(chat_id)
    winners = []
    
    for user_id, player in game['players'].items():
        card = player['card']
        card_type = player['card_type']
        marked = get_marked_cells(card, game['called_numbers'], card_type)
        
        if check_pattern(card, marked, PATTERNS[game['pattern']]):
            winners.append(user_id)
    
    return winners

def tournament_game_loop():
    """Game loop for multi-group tournament."""
    while daily_tournament['active'] and len(daily_tournament['called_numbers']) < 75:
        num = random.randint(1, 75)
        if num not in daily_tournament['called_numbers']:
            daily_tournament['called_numbers'].append(num)
            
            # Broadcast to all participating groups
            letter = get_bingo_letter(num)
            board = create_board(daily_tournament['called_numbers'])
            caption = f"🏆 *{letter}-{num}* Called ({len(daily_tournament['called_numbers'])}/75)\nTournament #{daily_tournament['game_id']}"
            
            for chat_id in daily_tournament['participating_groups']:
                try:
                    bot.send_photo(chat_id, board, caption=caption, parse_mode='Markdown')
                except Exception as e:
                    print(f"Failed to send to chat {chat_id}: {e}")
            
            # Jackpot boost every 10 numbers
            if len(daily_tournament['called_numbers']) % 10 == 0:
                daily_tournament['jackpot'] += 10
                msg = f"🔥 *TOURNAMENT HEAT!*\nJackpot now ${daily_tournament['jackpot']}"
                for chat_id in daily_tournament['participating_groups']:
                    try:
                        bot.send_message(chat_id, msg, parse_mode='Markdown')
                    except Exception as e:
                        print(f"Failed to send to chat {chat_id}: {e}")
            
            time.sleep(5)  # Slower pace for tournaments
    
    # Tournament ended without winner
    if daily_tournament['active']:
        daily_tournament['active'] = False
        end_msg = "🏁 *TOURNAMENT ENDED*\nNo winner this time. Better luck next tournament!"
        for chat_id in daily_tournament['participating_groups']:
            try:
                bot.send_message(chat_id, end_msg, parse_mode='Markdown')
            except Exception as e:
                print(f"Failed to send to chat {chat_id}: {e}")

@bot.message_handler(func=lambda m: True)
def echo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg_text = message.text.lower()
    
    # Check for tournament BINGO claim
    if 'tournament' in msg_text and 'bingo' in msg_text:
        if not daily_tournament['active']:
            bot.reply_to(message, "❌ No active tournament!")
            return
        
        if chat_id not in daily_tournament['players'] or user_id not in daily_tournament['players'][chat_id]:
            bot.reply_to(message, "❌ You haven't joined the tournament! Use /jointournament.")
            return
        
        player = daily_tournament['players'][chat_id][user_id]
        card = player['card']
        card_type = player['card_type']
        marked = get_marked_cells(card, daily_tournament['called_numbers'], card_type)
        
        # Verify winning pattern
        if check_pattern(card, marked, PATTERNS[daily_tournament['pattern']]):
            daily_tournament['active'] = False
            
            username = player['username']
            chat_title = message.chat.title or "Unknown Group"
            
            # Broadcast winner to all groups
            win_message = f"🏆 *TOURNAMENT WINNER!*\n\n"
            win_message += f"👤 Winner: {username}\n"
            win_message += f"🏠 From: {chat_title}\n"
            win_message += f"🎮 Tournament #{daily_tournament['game_id']}\n"
            win_message += f"🏅 Pattern: {daily_tournament['pattern'].replace('_', ' ').title()}\n"
            win_message += f"💰 Prize: ${daily_tournament['jackpot']}\n\n"
            win_message += "Congratulations! 🎉"
            
            for group_chat_id in daily_tournament['participating_groups']:
                try:
                    bot.send_message(group_chat_id, win_message, parse_mode='Markdown')
                except Exception as e:
                    print(f"Failed to send to chat {group_chat_id}: {e}")
            
            # Save to database
            conn = sqlite3.connect('game.db')
            c = conn.cursor()
            c.execute("INSERT INTO tournament_history (tournament_id, chat_id, winner_user_id, winner_name, prize) VALUES (?, ?, ?, ?, ?)",
                     (daily_tournament['game_id'], chat_id, user_id, username, daily_tournament['jackpot']))
            conn.commit()
            conn.close()
        else:
            bot.reply_to(message, "❌ Sorry, you don't have the winning pattern yet!")
        return
    
    # Check for regular group game BINGO claim
    if 'bingo' in msg_text:
        game = get_game_state(chat_id)
        
        if not game['active']:
            bot.reply_to(message, "❌ No active game!")
            return
        
        if user_id not in game['players']:
            bot.reply_to(message, "❌ You don't have a card! Use /getcard first.")
            return
        
        player = game['players'][user_id]
        card = player['card']
        card_type = player['card_type']
        marked = get_marked_cells(card, game['called_numbers'], card_type)
        
        # Check if player actually has the winning pattern
        if check_pattern(card, marked, PATTERNS[game['pattern']]):
            game['active'] = False
            
            username = message.from_user.first_name or message.from_user.username or "Player"
            win_message = f"🎉 *BINGO!*\n\n"
            win_message += f"Winner: {username}\n"
            win_message += f"Game #{game['game_id']}\n"
            win_message += f"Pattern: {game['pattern'].replace('_', ' ').title()}\n"
            win_message += f"💰 Prize: ${game['jackpot']}\n\n"
            win_message += "Congratulations! 🏆"
            
            bot.send_message(chat_id, win_message, parse_mode='Markdown')
            
            # Save to database
            conn = sqlite3.connect('game.db')
            c = conn.cursor()
            c.execute("INSERT INTO games (chat_id, numbers, winner, game_type, pattern) VALUES (?, ?, ?, ?, ?)",
                     (chat_id, ','.join(map(str, game['called_numbers'])), username, game['game_type'], game['pattern']))
            conn.commit()
            conn.close()
        else:
            bot.reply_to(message, "❌ Sorry, you don't have the winning pattern yet!")

# WEBHOOK - Render magic
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return jsonify(ok=True)

@app.route('/')
def home():
    return "🎰 Bingo Bot Live!"

if __name__ == '__main__':
    use_webhook = os.environ.get('USE_WEBHOOK', '0') == '1'
    if use_webhook:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        bot.infinity_polling()
