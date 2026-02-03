# 🚀 Deployment Guide

Complete guide for deploying the Bingo Bot to production environments.

## Table of Contents

- [Quick Deploy to Render](#quick-deploy-to-render)
- [Environment Variables](#environment-variables)
- [Deploy to Render (Web Dashboard)](#deploy-to-render-web-dashboard)
- [Deploy with Docker](#deploy-with-docker)
- [Deploy with GitHub Actions](#deploy-with-github-actions)
- [Post-Deployment Checklist](#post-deployment-checklist)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

---

## Quick Deploy to Render

**One-Click Deploy** (if you have Render account):

1. Click: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
2. Connect your GitHub repository
3. Set environment variables (see below)
4. Click "Create Web Service"
5. Wait for deployment (2-3 minutes)

---

## Environment Variables

### Required Variables

Set these in your deployment platform:

| Variable | Description | Example | Where to Get |
|----------|-------------|---------|--------------|
| `BOT_TOKEN` | Telegram bot token | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` | [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | Your Telegram user ID | `123456789` | [@userinfobot](https://t.me/userinfobot) |

### Optional Variables

| Variable | Description | Default | When Needed |
|----------|-------------|---------|-------------|
| `PLAYER_DATA_GROUP_ID` | Private group for logging | Not set | For audit trail logging |
| `PYTHON_VERSION` | Python runtime version | `3.11.0` | Platform-specific |

### How to Get Variables

**BOT_TOKEN**:
1. Open Telegram
2. Search for [@BotFather](https://t.me/BotFather)
3. Send `/newbot`
4. Follow instructions
5. Copy the token

**ADMIN_ID**:
1. Open Telegram
2. Search for [@userinfobot](https://t.me/userinfobot)
3. Send `/start`
4. Copy your ID

**PLAYER_DATA_GROUP_ID** (optional):
1. Create a private group
2. Add your bot as administrator
3. Forward a message from the group to [@userinfobot](https://t.me/userinfobot)
4. Copy the chat ID (negative number)

---

## Deploy to Render (Web Dashboard)

Render is a free hosting platform perfect for this bot.

### Step 1: Prepare Repository

Your repository is already configured! It includes:
- ✅ `render.yaml` - Render configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `Procfile` - Process commands

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Grant access to your repository

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `shawtybaby671-ai/bingo-bot-free`
3. Configure:
   - **Name**: `bingo-bot` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your deployment branch)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free

### Step 4: Add Environment Variables

In the Render dashboard:

1. Scroll to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add each variable:
   ```
   BOT_TOKEN = your_bot_token_here
   ADMIN_ID = your_telegram_id_here
   ```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for build (2-3 minutes)
3. Check logs for "Bot started successfully"
4. Test your bot in Telegram!

### Step 6: Configure Auto-Deploy

1. Go to your service settings
2. Under **"Build & Deploy"**
3. Enable **"Auto-Deploy"** from main branch
4. Every push will now auto-deploy!

---

## Deploy with Docker

### Local Docker Testing

```bash
# Build the image
docker build -t bingo-bot .

# Run with environment variables
docker run -d \
  --name bingo-bot \
  -e BOT_TOKEN="your_token" \
  -e ADMIN_ID="your_id" \
  -v $(pwd)/player_data:/app/player_data \
  -v $(pwd)/game.db:/app/game.db \
  bingo-bot

# View logs
docker logs -f bingo-bot

# Stop container
docker stop bingo-bot

# Remove container
docker rm bingo-bot
```

### Deploy to Docker Hub

```bash
# Tag your image
docker tag bingo-bot yourusername/bingo-bot:latest

# Push to Docker Hub
docker push yourusername/bingo-bot:latest
```

### Deploy with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bingo-bot:
    build: .
    container_name: bingo-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - PLAYER_DATA_GROUP_ID=${PLAYER_DATA_GROUP_ID}
    volumes:
      - ./player_data:/app/player_data
      - ./game.db:/app/game.db
    env_file:
      - .env
```

Then run:

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## Deploy with GitHub Actions

### Automatic Deployment on Push

The repository includes a CI/CD workflow that:
- ✅ Runs tests on every push
- ✅ Validates code quality
- ✅ Can auto-deploy to Render

### Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add secrets:
   - `BOT_TOKEN` - Your bot token
   - `ADMIN_ID` - Your admin ID
   - `RENDER_API_KEY` - Your Render API key (optional)
   - `RENDER_SERVICE_ID` - Your Render service ID (optional)

### Manual Deployment Trigger

The workflow supports manual deployment:

1. Go to **Actions** tab
2. Select **"Python package"** workflow
3. Click **"Run workflow"**
4. Choose branch and run

---

## Deploy to Other Platforms

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create bingo-bot-app

# Set environment variables
heroku config:set BOT_TOKEN="your_token"
heroku config:set ADMIN_ID="your_id"

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Add environment variables
5. Deploy automatically!

### DigitalOcean App Platform

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Create new app from GitHub
3. Select repository
4. Configure environment variables
5. Deploy!

### Linux VPS (systemd)

Create service file `/etc/systemd/system/bingo-bot.service`:

```ini
[Unit]
Description=Bingo Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/bingo-bot-free
Environment="BOT_TOKEN=your_token"
Environment="ADMIN_ID=your_id"
ExecStart=/home/youruser/bingo-bot-free/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable bingo-bot

# Start service
sudo systemctl start bingo-bot

# Check status
sudo systemctl status bingo-bot

# View logs
sudo journalctl -u bingo-bot -f
```

---

## Post-Deployment Checklist

After deploying, verify everything works:

- [ ] Bot responds to `/start` command
- [ ] Admin commands work (`/approvegroup`, `/schedulegame`)
- [ ] Players can see menu buttons
- [ ] Card generation works (`/getcard`)
- [ ] Database persists data
- [ ] Player data logging works (if configured)
- [ ] Status command shows game info
- [ ] Winners are detected correctly

### Test Commands

```
/start - Should show menu
/menu - Should show menu buttons
/profile - Should show player profile
/schedule - Should show scheduled games
/help - Should show help text
```

### Admin Test Commands

```
/approvegroup - In a group (as admin)
/schedulegame 2026-02-10 18:00 classic single_line 10 - Schedule game
/startgame classic single_line 100 - Start group game
/starttournament classic blackout 500 - Start tournament
```

---

## Monitoring and Maintenance

### View Logs

**Render**:
1. Go to your service dashboard
2. Click **"Logs"** tab
3. View real-time logs

**Docker**:
```bash
docker logs -f bingo-bot
```

**Systemd**:
```bash
sudo journalctl -u bingo-bot -f
```

### Monitor Health

Check if bot is running:

```bash
# Test bot is responding
# Send /start to your bot in Telegram
```

### Database Backup

**Automatic** (Render with disk):
- Render backs up disk automatically

**Manual**:
```bash
# Download database
scp user@server:/path/to/game.db ./game.db.backup

# Or use Render CLI
render disk snapshot create
```

### Update Deployment

**Render** (with auto-deploy enabled):
```bash
git push origin main
# Automatically deploys!
```

**Docker**:
```bash
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

**Systemd**:
```bash
# Pull latest code
git pull

# Restart service
sudo systemctl restart bingo-bot
```

---

## Troubleshooting

### Bot Not Responding

**Problem**: Bot doesn't respond to commands

**Solutions**:
1. Check logs for errors
2. Verify `BOT_TOKEN` is correct
3. Ensure bot is running
4. Check network connectivity
5. Verify webhook is not set (for polling mode)

```python
# Disable webhook if set
import requests
BOT_TOKEN = "your_token"
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
```

### Environment Variables Not Loading

**Problem**: Bot can't find environment variables

**Solutions**:
1. Verify variables are set in platform
2. Check variable names (case-sensitive)
3. Restart service after adding variables
4. Use `.env` file for local testing

### Database Permission Errors

**Problem**: Can't write to database

**Solutions**:
1. Check disk is mounted (Render)
2. Verify write permissions
3. Check disk space
4. Ensure database path is correct

### Build Failures

**Problem**: Deployment build fails

**Solutions**:
1. Check `requirements.txt` is valid
2. Verify Python version compatibility
3. Check build logs for specific errors
4. Ensure all dependencies are available

### Memory Issues

**Problem**: Service crashes due to memory

**Solutions**:
1. Upgrade plan (Free → Starter)
2. Optimize database queries
3. Clear old data periodically
4. Monitor memory usage

### Rate Limiting

**Problem**: Telegram API rate limits

**Solutions**:
1. Add delays between API calls
2. Use batch operations
3. Cache frequent requests
4. Implement exponential backoff

---

## Security Best Practices

### Environment Variables

- ✅ **Never** commit tokens to Git
- ✅ Use platform secret management
- ✅ Rotate tokens periodically
- ✅ Use different tokens for dev/prod

### Database

- ✅ Enable backups
- ✅ Don't expose database publicly
- ✅ Regular data cleanup
- ✅ Monitor access logs

### Bot Permissions

- ✅ Only add necessary group permissions
- ✅ Verify admin before privileged operations
- ✅ Log all admin actions
- ✅ Rate limit user requests

---

## Cost Estimation

### Free Tier Options

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| **Render** | Yes | 750 hours/month, 1 service |
| **Railway** | $5 credit | Usage-based after credit |
| **Fly.io** | Yes | 3 shared-cpu VMs |
| **Heroku** | No | Starting at $7/month |

### Recommended for Production

- **Free hobby**: Render Free
- **Small scale**: Render Starter ($7/month)
- **Medium scale**: Render Standard ($25/month)
- **Large scale**: Dedicated VPS ($5-20/month)

---

## Support

### Getting Help

1. Check [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) for local setup
2. Check [README.md](README.md) for features
3. Review logs for error messages
4. Search GitHub issues
5. Create new issue with:
   - Error message
   - Steps to reproduce
   - Platform used
   - Log excerpts

### Useful Resources

- [Render Documentation](https://render.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)

---

## Success! 🎉

Your bot should now be deployed and running!

**Next Steps**:
1. Add bot to your Telegram groups
2. Approve groups with `/approvegroup`
3. Schedule your first game
4. Invite players
5. Have fun!

**Remember**: Free tiers may sleep after inactivity. First request after sleep may be slow (20-30 seconds).
