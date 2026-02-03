# 🚀 Launch Guide - Bingo Bot

Complete guide to launching and running the Bingo Bot locally or in production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Getting Your Bot Token](#getting-your-bot-token)
- [Getting Your Admin ID](#getting-your-admin-id)
- [Local Development Setup](#local-development-setup)
- [Running Locally](#running-locally)
- [Deploying to Render](#deploying-to-render)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, make sure you have:

- **Python 3.8+** installed on your system
- **pip** (Python package manager)
- A **Telegram account**
- Basic knowledge of terminal/command line

### Check Your Python Version
```bash
python --version
# or
python3 --version
```

Should show Python 3.8 or higher.

---

## Getting Your Bot Token

### Step 1: Create a Bot with BotFather

1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/newbot`
3. Follow the prompts:
   - Give your bot a **name** (e.g., "My Bingo Bot")
   - Give your bot a **username** (must end in 'bot', e.g., "mybingo_bot")
4. BotFather will give you a **token** that looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. **Save this token** - you'll need it to run the bot

### Important: Keep Your Token Secret!
- Never share your bot token publicly
- Don't commit it to GitHub
- Use environment variables to store it

---

## Getting Your Admin ID

Your Telegram user ID is needed so the bot knows who the admin is.

### Method 1: Using @userinfobot
1. Search for **@userinfobot** in Telegram
2. Start the bot
3. It will reply with your user ID (e.g., `123456789`)

### Method 2: Using @raw_info_bot
1. Search for **@raw_info_bot** in Telegram
2. Start the bot
3. Look for the `id` field in the response

### Method 3: Using Your Own Bot
1. Start your bot (see Running Locally section below)
2. Send any message to your bot
3. Check the console logs for your user ID

**Save your user ID** - you'll use it as `ADMIN_ID`.

---

## Local Development Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/shawtybaby671-ai/bingo-bot-free.git
cd bingo-bot-free
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `pyTelegramBotAPI` - Telegram bot framework
- `Flask` - Web framework (for webhooks)
- `gunicorn` - WSGI server (for production)
- `Pillow` - Image processing

### Step 4: Set Up Environment Variables

#### Option A: Using .env file (Recommended for local)

1. Create a `.env` file in the project root:
```bash
touch .env
```

2. Add your credentials:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
PLAYER_DATA_GROUP_ID=-1001234567890
USE_WEBHOOK=0
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

4. Add to the top of `bot.py` (after imports):
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Option B: Export in Terminal (Quick testing)

```bash
# On macOS/Linux
export BOT_TOKEN="your_bot_token_here"
export ADMIN_ID="your_telegram_user_id"

# On Windows Command Prompt
set BOT_TOKEN=your_bot_token_here
set ADMIN_ID=your_telegram_user_id

# On Windows PowerShell
$env:BOT_TOKEN="your_bot_token_here"
$env:ADMIN_ID="your_telegram_user_id"
```

---

## Running Locally

### Step 1: Start the Bot
```bash
python bot.py
```

Or if you're using Python 3 specifically:
```bash
python3 bot.py
```

### Step 2: Verify It's Running
You should see output like:
```
Starting bot in polling mode...
Bot is running!
```

### Step 3: Test Your Bot
1. Open Telegram
2. Search for your bot's username
3. Send `/start` command
4. You should see the welcome message with inline buttons!

### Stopping the Bot
Press `Ctrl+C` in the terminal to stop the bot.

---

## Deploying to Render

Render provides **free hosting** for the bot!

### Prerequisites
- GitHub account
- Render account (sign up at [render.com](https://render.com))
- Your code pushed to GitHub

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create a New Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"** or **"Background Worker"**
3. Connect your GitHub account
4. Select your `bingo-bot-free` repository

### Step 3: Configure the Service

**Basic Settings:**
- **Name**: `bingo-bot` (or any name you like)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`

**Advanced Settings:**
- **Instance Type**: Free (for testing)
- **Auto-Deploy**: Yes (recommended)

### Step 4: Add Environment Variables

In the Render dashboard, add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `BOT_TOKEN` | `your_bot_token` | From BotFather |
| `ADMIN_ID` | `your_user_id` | Your Telegram user ID |
| `PLAYER_DATA_GROUP_ID` | `-1001234567890` | Optional: Private group for logging |
| `USE_WEBHOOK` | `0` | Use polling mode (recommended for free tier) |

### Step 5: Deploy
1. Click **"Create Web Service"** or **"Create Worker"**
2. Render will automatically build and deploy your bot
3. Check the logs to ensure it started successfully

### Step 6: Verify Deployment
1. Open Telegram
2. Send `/start` to your bot
3. It should respond immediately!

---

## Environment Variables

Complete list of environment variables:

### Required Variables

#### `BOT_TOKEN`
- **Description**: Your Telegram bot token from BotFather
- **Example**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Required**: Yes
- **Get it from**: [@BotFather](https://t.me/BotFather)

#### `ADMIN_ID`
- **Description**: Your Telegram user ID (admin of the bot)
- **Example**: `123456789`
- **Required**: Yes
- **Get it from**: [@userinfobot](https://t.me/userinfobot)

### Optional Variables

#### `PLAYER_DATA_GROUP_ID`
- **Description**: Chat ID of private group for logging player data
- **Example**: `-1001234567890`
- **Required**: No
- **Default**: None (file logging only)
- **How to get**: 
  1. Create a private Telegram group
  2. Add your bot as admin
  3. Forward a message from the group to [@userinfobot](https://t.me/userinfobot)

#### `USE_WEBHOOK`
- **Description**: Whether to use webhook mode (vs polling)
- **Example**: `0` or `1`
- **Required**: No
- **Default**: `0` (polling mode)
- **Note**: Use `0` for local development and free hosting

#### `PORT`
- **Description**: Port for webhook server (if USE_WEBHOOK=1)
- **Example**: `5000`
- **Required**: Only if USE_WEBHOOK=1
- **Default**: `5000`

---

## Troubleshooting

### Bot Doesn't Respond

**Problem**: Bot doesn't reply to messages

**Solutions**:
1. Check bot is running: Look for "Bot is running!" in console
2. Verify BOT_TOKEN: Make sure it's correct and active
3. Check bot isn't stopped: Search your bot on Telegram, click "Start"
4. Review logs: Look for error messages in console

### "Invalid BOT_TOKEN" Error

**Problem**: Bot fails to start with authentication error

**Solutions**:
1. Verify your BOT_TOKEN is correct
2. Check for extra spaces or quotes in the token
3. Make sure you copied the entire token
4. Generate a new token with BotFather if needed

### "Connection Error" or "Network Error"

**Problem**: Bot can't connect to Telegram

**Solutions**:
1. Check your internet connection
2. Try using a VPN if Telegram is blocked in your region
3. Check if Telegram servers are down: [status.telegram.org](https://status.telegram.org)
4. Wait a few minutes and try again

### Database Errors

**Problem**: Errors related to `game.db`

**Solutions**:
1. Delete `game.db` file and restart bot (will recreate it)
2. Check file permissions (bot needs write access)
3. Make sure you have enough disk space

### Import Errors

**Problem**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
1. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```
2. Make sure you're in the virtual environment (if using one)
3. Check Python version is 3.8 or higher

### Permission Errors

**Problem**: Bot can't write to `player_data/` directory

**Solutions**:
1. Check folder permissions:
   ```bash
   chmod 755 player_data/
   ```
2. Make sure the folder exists:
   ```bash
   mkdir -p player_data
   ```

### Bot Commands Not Working

**Problem**: Commands like `/start` don't work

**Solutions**:
1. Make sure you're admin (check ADMIN_ID)
2. Some commands require approved groups
3. Check bot has proper permissions in groups
4. Restart the bot

### Webhook Issues (If USE_WEBHOOK=1)

**Problem**: Bot doesn't receive updates via webhook

**Solutions**:
1. Switch to polling mode (USE_WEBHOOK=0) for local development
2. For production webhooks, ensure:
   - HTTPS is enabled
   - Certificate is valid
   - Webhook URL is accessible
   - PORT is set correctly

---

## Advanced Configuration

### Running with Gunicorn (Production)

If you want to use webhook mode with gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 bot:app
```

### Running as a Background Service (Linux)

Create a systemd service file `/etc/systemd/system/bingo-bot.service`:

```ini
[Unit]
Description=Bingo Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/bingo-bot-free
Environment="BOT_TOKEN=your_token"
Environment="ADMIN_ID=your_id"
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable bingo-bot
sudo systemctl start bingo-bot
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t bingo-bot .
docker run -e BOT_TOKEN="your_token" -e ADMIN_ID="your_id" bingo-bot
```

---

## Quick Reference

### Start Bot Locally
```bash
python bot.py
```

### Stop Bot
Press `Ctrl+C`

### View Logs (Render)
Go to your service dashboard → Logs tab

### Restart Bot (Render)
Service dashboard → Manual Deploy → Deploy Latest Commit

### Clear Database
```bash
rm game.db
# Bot will recreate it on next start
```

### Update Bot
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python bot.py
```

---

## Getting Help

If you're still having issues:

1. **Check the logs** for error messages
2. **Review documentation**: 
   - README.md
   - PLAYER_DATA_LOGGING.md
   - INLINE_MENU_FLOW.md
3. **Search existing issues** on GitHub
4. **Open a new issue** with:
   - What you were trying to do
   - What happened instead
   - Error messages (if any)
   - Your setup (OS, Python version, etc.)

---

## Success! 🎉

If you've made it here and your bot is running, congratulations! Your bot is now live and ready to play bingo!

**Next Steps**:
- Invite the bot to your Telegram groups
- Use `/approvegroup` to approve groups for games
- Schedule games with `/schedulegame`
- Explore all the features in the README.md

Enjoy your bingo bot! 🎰
