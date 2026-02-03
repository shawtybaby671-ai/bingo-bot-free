# 🎰 Free Bingo Bot

A comprehensive Telegram bingo bot with inline menu system, player profiles, game scheduling, and proper 75-ball bingo rules.

## ✨ New Features

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

## 💎 Points System

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

## Deployed on Render
FREE FOREVER
