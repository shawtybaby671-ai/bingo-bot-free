# 🚀 Quick Deployment Guide

**Get your bot deployed in under 5 minutes!**

## Option 1: Deploy to Render (Easiest - Free) ⭐

### 1. Get Credentials (2 minutes)

**Bot Token:**
1. Open Telegram → Search `@BotFather`
2. Send `/newbot`
3. Follow prompts
4. Copy token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Admin ID:**
1. Open Telegram → Search `@userinfobot`
2. Send `/start`
3. Copy your ID (looks like: `123456789`)

### 2. Deploy to Render (2 minutes)

1. **Click button:** [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

2. **Sign in** with GitHub (if not already)

3. **Create new** → **Web Service**

4. **Connect** your GitHub repository: `shawtybaby671-ai/bingo-bot-free`

5. **Configure:**
   - Name: `bingo-bot` (or your choice)
   - Region: Choose closest to you
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`

6. **Add Environment Variables:**
   - Click "Advanced"
   - Add: `BOT_TOKEN` = `your_token_here`
   - Add: `ADMIN_ID` = `your_id_here`

7. **Create Web Service** (wait 2-3 minutes)

### 3. Test Your Bot (1 minute)

1. Open Telegram
2. Search for your bot (the name you gave to BotFather)
3. Send `/start`
4. You should see the interactive menu! 🎉

**Done! Your bot is live!** 🚀

---

## Option 2: Deploy with Docker 🐳

### Prerequisites
- Docker installed on your machine

### Quick Start

```bash
# Clone repository
git clone https://github.com/shawtybaby671-ai/bingo-bot-free.git
cd bingo-bot-free

# Build image
docker build -t bingo-bot .

# Run container (replace with your credentials)
docker run -d \
  --name bingo-bot \
  -e BOT_TOKEN="your_bot_token_here" \
  -e ADMIN_ID="your_admin_id_here" \
  -v $(pwd)/player_data:/app/player_data \
  -v $(pwd)/game.db:/app/game.db \
  bingo-bot

# View logs
docker logs -f bingo-bot
```

**Using docker-compose:**

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any editor

# Start service
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Option 3: Local Development 💻

### Quick Setup

```bash
# Clone repository
git clone https://github.com/shawtybaby671-ai/bingo-bot-free.git
cd bingo-bot-free

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # Add BOT_TOKEN and ADMIN_ID

# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

**With Virtual Environment (Recommended):**

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

**Using Scripts:**

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

---

## Option 4: Visual Studio Code 🎨

### Setup in VS Code

1. **Open folder** in VS Code:
   ```bash
   code bingo-bot-free
   ```

2. **Install recommended extensions** (popup will appear)

3. **Open Terminal** in VS Code (Ctrl+`)

4. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env`** with your credentials

6. **Press F5** to start debugging!

**Or use Tasks:**
- Press `Ctrl+Shift+B` to start bot
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Full Setup (First Time)"

**See [VS_CODE_SETUP.md](VS_CODE_SETUP.md) for complete VS Code guide.**

---

## Verify Deployment ✅

### Test Commands

Open your bot in Telegram and test:

```
/start          → Should show interactive menu
/menu           → Should show menu buttons
/profile        → Should show your profile
/help           → Should show help text
```

### Admin Commands (as admin)

```
/approvegroup   → In a group (approves the group)
/schedulegame   → Schedule a game
/startgame      → Start immediate game
```

### Success Indicators

- ✅ Bot responds to `/start`
- ✅ Menu buttons appear
- ✅ Profile loads
- ✅ No errors in logs
- ✅ Database file created (`game.db`)

---

## Troubleshooting 🔧

### Bot Doesn't Respond

**Check:**
1. Bot token is correct
2. Bot is running (check logs)
3. No webhook set (use polling mode)

**Fix:**
```python
# Remove webhook if set
import requests
BOT_TOKEN = "your_token"
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
```

### Environment Variables Not Loading

**Check:**
1. `.env` file exists
2. Variables are set (no spaces around `=`)
3. Service restarted after setting variables

**Example `.env`:**
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
```

### Import Errors

**Fix:**
```bash
pip install -r requirements.txt
```

### Port Already in Use (local)

**Fix:**
```bash
# Find process
lsof -i :5000  # or netstat -ano | findstr :5000 on Windows

# Kill process
kill -9 <PID>
```

---

## Next Steps 🎯

1. **Read documentation:**
   - [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) - Complete setup guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
   - [README.md](README.md) - Features and commands

2. **Add bot to groups:**
   - Add bot to your Telegram group
   - Make bot admin
   - Use `/approvegroup` to enable games

3. **Schedule first game:**
   ```
   /schedulegame 2026-02-10 18:00 classic single_line 10
   ```

4. **Invite players:**
   - Share bot link
   - Players can join via menu
   - Schedule regular games

5. **Monitor:**
   - Check logs regularly
   - Monitor bot uptime
   - Review player feedback

---

## Support 💬

**Documentation:**
- [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) - Local setup
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [VS_CODE_SETUP.md](VS_CODE_SETUP.md) - VS Code setup
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment checklist

**Issues:**
- GitHub: [Create an issue](https://github.com/shawtybaby671-ai/bingo-bot-free/issues)

**Resources:**
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Render Documentation](https://render.com/docs)
- [Docker Documentation](https://docs.docker.com/)

---

## Cost 💰

### Free Options

- **Render Free Tier**: 750 hours/month (enough for 24/7!)
- **Docker Local**: Free (uses your machine)
- **Railway**: $5 credit to start

### Paid Options

- **Render Starter**: $7/month (better performance)
- **Heroku Eco**: $7/month
- **VPS (DigitalOcean)**: $5+/month

**Recommendation**: Start with Render Free tier! It's perfect for hobby use.

---

## Success! 🎉

Your bot should now be running!

**What you can do:**
- ✅ Play bingo in Telegram groups
- ✅ Schedule games in advance
- ✅ Track player points
- ✅ Run tournaments
- ✅ Approve game registrations
- ✅ Log player data

**Have fun!** 🎊

---

**Quick Links:**
- [Deploy to Render](https://render.com/deploy) ⚡
- [Full Documentation](README.md) 📚
- [Report Issues](https://github.com/shawtybaby671-ai/bingo-bot-free/issues) 🐛
