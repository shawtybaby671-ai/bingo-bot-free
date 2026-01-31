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

# Game State
game_active = False
called_numbers = []
players = {}
jackpot = 0
current_game_id = 0

# Database
def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games 
                 (id INTEGER PRIMARY KEY, numbers TEXT, winner TEXT)''')
    conn.commit()
    conn.close()
init_db()

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
    bot.reply_to(message, "🎰 *Bingo Bot Online!*\n/startgame - New game\n/status - Check game", parse_mode='Markdown')

@bot.message_handler(commands=['startgame'])
def start_game(message):
    global game_active, called_numbers, current_game_id, jackpot
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only")
        return
        
    game_active = True
    called_numbers = []
    current_game_id += 1
    jackpot += 10
    
    bot.send_message(message.chat.id, f"🎮 *GAME #{current_game_id} STARTED*\n💰 Jackpot: ${jackpot}", parse_mode='Markdown')
    threading.Thread(target=game_loop, args=(message.chat.id,)).start()

@bot.message_handler(commands=['status'])
def status(message):
    if not game_active:
        bot.reply_to(message, "❌ No active game")
        return
    status_text = f"🎯 *Game Active*\n📊 Called: {len(called_numbers)}/75\n💰 Jackpot: ${jackpot}"
    bot.reply_to(message, status_text, parse_mode='Markdown')

def game_loop(chat_id):
    global game_active, called_numbers, jackpot
    while game_active and len(called_numbers) < 75:
        num = random.randint(1, 75)
        if num not in called_numbers:
            called_numbers.append(num)
            
            # Send board + number
            board = create_board(called_numbers)
            bot.send_photo(chat_id, board, caption=f"🎱 *B{num}* Called {len(called_numbers)}/75")
            
            # Check winners (simple)
            if len(called_numbers) % 10 == 0:
                bot.send_message(chat_id, f"🔥 *HOT NUMBERS!*\nJackpot now ${jackpot + 5}")
                jackpot += 5
            
            time.sleep(3)
    
    game_active = False
    bot.send_message(chat_id, "🏁 *GAME OVER*\nNew game soon!")

@bot.message_handler(func=lambda m: True)
def echo(message):
    if 'bingo' in message.text.lower():
        bot.reply_to(message, "🎉 BINGO! You win $" + str(random.randint(10, 100)))

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
