from flask import Flask, request, jsonify
import telebot
import os
import random
import io
from PIL import Image, ImageDraw
import sqlite3
import threading
import time

app = Flask(__name__)

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

@bot.message_handler(commands=['start'])
def start(message):
    help_text = "🎰 *Bingo Bot Online!*\n\n"
    help_text += "*Player Commands:*\n"
    help_text += "/getcard - Get bingo card (group game)\n"
    help_text += "/mycard - View your card\n"
    help_text += "/status - Check group game status\n"
    help_text += "/jointournament - Join daily tournament\n"
    help_text += "/tournamentcard - View tournament card\n"
    help_text += "/tournamentstatus - Check tournament status\n\n"
    
    if message.from_user.id == ADMIN_ID:
        help_text += "*Admin Commands:*\n"
        help_text += "/startgame [type] [pattern] - Start group game\n"
        help_text += "/starttournament [type] [pattern] - Start multi-group tournament\n"
        help_text += "/approvegroup - Approve this group\n"
        help_text += "/unapprovegroup - Remove group approval\n"
        help_text += "/listgroups - List approved groups\n"
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

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
