# 🎰 Free Bingo Bot

A comprehensive Telegram bingo bot with inline menu system, player profiles, game scheduling, proper 75-ball bingo rules, and **automated player data logging**.

## 🚀 How to Launch

**Quick Start:**
1. Get your bot token from [@BotFather](https://t.me/BotFather)
2. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)
3. Set environment variables: `BOT_TOKEN` and `ADMIN_ID`
4. Run: `python bot.py`

**📖 Detailed Instructions:** See [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) for complete setup instructions including:
- Local development setup
- Getting credentials
- Environment variable configuration
- Deploying to Render (free hosting)
- Troubleshooting common issues

## ✨ New Features

### 📊 Player Data Logging (NEW!)
- **File-based storage**: All player-admin DM conversations saved as JSON files
- **Private group logging**: Optional logging to a private Telegram group
- **Audit trail**: Complete history of registrations, approvals, and interactions
- **Admin commands**: Manual logging with `/loguser`, `/logreg`, `/logdm`

### 🎮 Individual Player Bot with Inline Menu
- **Interactive Menu System**: Use inline buttons to navigate
- **Player Profiles**: Track points, cards owned, and game history
- **Game Scheduling**: View and join upcoming scheduled games
- **Card Purchase System**: Buy multiple cards with points
- **Admin Approval Workflow**: DM-based approval system for game registrations

## Features

### 🎮 Game Modes
- **Per-Group Games**: Each approved group can run independent bingo games
- **Daily Tournaments**: Multi-group competitions where all approved groups play together
- **Scheduled Games**: Pre-scheduled games that players can register for in advance

### 🎲 Card Types
- **Classic**: Single number per cell (traditional bingo)
- **Dual Action**: Two numbers per cell (mark with either number)

### 🏆 Winning Patterns
- Single Line (horizontal, vertical, diagonal)
- Four Corners
- Blackout (full card)
- Letter X
- Postage Stamp (2x2 corner blocks)

## 🚀 Quick Start Guide

### For Players

1. **Start the bot**: Send `/start` or `/menu` to see the main menu
2. **View your profile**: Click "👤 Player Profile" to see your points and stats
3. **Browse games**: Click "📅 Game Schedule" to see upcoming games
4. **Join a game**:
   - Click "🎯 Join a Game"
   - Select the game you want to join
   - Choose how many cards (1-6)
   - Review the points required
   - Click "✅ Approve" if you have enough points
5. **Complete registration**:
   - Click "💬 Open DM with Bot"
   - Click Start in the DM
   - Wait for admin approval
6. **Play the game**: Once approved, you'll receive your cards when the game starts!

### Player Menu Options

**👤 Player Profile**
- View your username, points balance, and cards owned
- Track your player ID

**📋 Commands**
- See list of all available commands
- Quick reference guide

**📖 Rules**
- Learn how to play bingo
- Understand card types and winning patterns
- See the game workflow

**🎮 Request Game Type**
- Request specific game types (Classic or Dual Action)
- Admin gets notified of your preference

**📅 Game Schedule**
- View all upcoming scheduled games
- See game details: date, time, type, pattern, entry cost

**🎯 Join a Game**
- Browse available games
- Select number of cards to purchase
- Confirm purchase with points
- Get added to the game after admin approval

## Commands

### Player Commands
- `/start` or `/menu` - Show main menu with inline buttons
- `/command` - Display commands list
- `/profile` - View your player profile
- `/schedule` - View upcoming games schedule
- `/getcard` - Get your card for group game
- `/mycard` - View your current card
- `/status` - Check group game status
- `/jointournament` - Join the daily tournament
- `/tournamentcard` - View your tournament card
- `/tournamentstatus` - Check tournament status

### Admin Commands
- `/schedulegame <date> <time> <type> <pattern> [cost]` - Schedule a new game
  - Example: `/schedulegame 2026-02-10 18:00 classic single_line 10`
- `/startgame [type] [pattern]` - Start a group game
- `/starttournament [type] [pattern]` - Start multi-group tournament
- `/approvegroup` - Approve current group for games
- `/unapprovegroup` - Remove group approval
- `/listgroups` - List all approved groups

#### Player Data Logging Commands (NEW!)
- `/loguser <user_id>` - Log user profile to private group
- `/logreg <registration_id>` - Log registration details to private group
- `/logdm <user_id> <registration_id>` - Log DM conversation history to private group

**Note**: Private group logging requires `PLAYER_DATA_GROUP_ID` environment variable to be set.

## 📊 Player Data Management

### Automatic Logging
The bot automatically logs all player interactions:

**File-based Storage** (`player_data/` directory):
- `player_{user_id}_reg_{registration_id}.json` - DM conversation history
- `player_{user_id}_profile.json` - Player profile snapshots

**Private Group Logging** (optional):
- Set `PLAYER_DATA_GROUP_ID` environment variable to your private group/channel ID
- Bot will automatically log all registrations, approvals, and interactions
- Messages include searchable hashtags: `#user_{id}`, `#reg_{id}`, `#approved`, `#rejected`
- Admin can review/search through group chat history

### Data Structure

**DM Conversation Files**:
```json
{
  "user_id": 12345,
  "registration_id": 501,
  "created_at": "2026-02-03T10:00:00",
  "last_updated": "2026-02-03T10:15:00",
  "messages": [
    {
      "timestamp": "2026-02-03T10:00:00",
      "type": "registration_request",
      "data": { "game_id": 1, "cards_requested": 3, ... }
    },
    {
      "timestamp": "2026-02-03T10:15:00",
      "type": "admin_approval",
      "data": { "approved": true, "admin_name": "Admin", ... }
    }
  ]
}
```

**Profile Snapshot Files**:
```json
{
  "user_id": 12345,
  "username": "PlayerName",
  "created_at": "2026-02-03T09:00:00",
  "last_updated": "2026-02-03T10:15:00",
  "registrations": [
    {
      "timestamp": "2026-02-03T10:00:00",
      "registration_id": 501,
      "game_id": 1,
      "status": "confirmed",
      ...
    }
  ]
}
```

### Environment Variables

- **Starting Balance**: 100 points for new players
- **Game Entry**: Each card costs points (set by admin per game)
- **Points Deduction**: Only deducted after admin approves your registration
- **Check Balance**: Use `/profile` or click "Player Profile" in menu

## 🎯 Registration & Approval Workflow

1. **Player selects game and cards** → Points are calculated
2. **Player approves purchase** → Registration created (points not yet deducted)
3. **Player DMs bot** → Approval request sent to admin
4. **Admin reviews request** → Admin sees player info, game details, points required
5. **Admin approves** → Points deducted, player added to game
6. **Player receives cards** → When the scheduled game starts

## Game Types
- `classic` - Traditional single-number cards
- `dual_action` - Two numbers per cell (default: classic)

## Pattern Options
- `single_line` - Any line (row, column, diagonal)
- `four_corners` - All four corner cells
- `blackout` - Complete card coverage
- `letter_X` - Both diagonals
- `postage_stamp` - 2x2 corner block

## BINGO Number System
- **B**: 1-15
- **I**: 16-30
- **N**: 31-45 (center is FREE space)
- **G**: 46-60
- **O**: 61-75

## 🗄️ Database Schema

### Player Profiles
- Stores user ID, username, points balance, cards owned
- Auto-created on first interaction

### Scheduled Games
- Game date, time, type, pattern, max players, entry cost
- Admin creates via `/schedulegame`

### Game Registrations
- Links players to scheduled games
- Tracks cards requested, points paid, approval status
- Requires admin approval via DM workflow

## 🔧 Environment Variables

### Required
- `BOT_TOKEN` - Your Telegram bot token from @BotFather
- `ADMIN_ID` - Telegram user ID of the bot admin

### Optional
- `PLAYER_DATA_GROUP_ID` - Chat ID of private group for logging player data
  - Create a private group/channel
  - Add your bot as administrator
  - Get the chat ID (use `/getid` bot or forward message to @userinfobot)
  - Set this environment variable to enable group logging
  - Example: `-1001234567890`

## 📚 Documentation

- **[LAUNCH_GUIDE.md](LAUNCH_GUIDE.md)** - Complete setup and deployment guide
- **[PLAYER_DATA_LOGGING.md](PLAYER_DATA_LOGGING.md)** - Player data logging system documentation
- **[INLINE_MENU_FLOW.md](INLINE_MENU_FLOW.md)** - User flow and menu navigation
- **[DATA_FLOW_DIAGRAM.md](DATA_FLOW_DIAGRAM.md)** - System architecture and data flow

## Deployed on Render
FREE FOREVER
