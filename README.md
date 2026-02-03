# 🎰 Free Bingo Bot

A comprehensive Telegram bingo bot with proper 75-ball rules, per-group games, and multi-group tournaments.

## Features

### 🎮 Game Modes
- **Per-Group Games**: Each approved group can run independent bingo games
- **Daily Tournaments**: Multi-group competitions where all approved groups play together

### 🎲 Card Types
- **Classic**: Single number per cell (traditional bingo)
- **Dual Action**: Two numbers per cell (mark with either number)

### 🏆 Winning Patterns
- Single Line (horizontal, vertical, diagonal)
- Four Corners
- Blackout (full card)
- Letter X
- Postage Stamp (2x2 corner blocks)

## How to Play

### Getting Started
1. Admin must first approve your group: `/approvegroup`
2. Wait for a game to start or join a tournament

### For Per-Group Games
1. **Admin starts game**: `/startgame [classic|dual_action] [pattern]`
   - Example: `/startgame classic single_line`
2. **Get your card**: `/getcard`
   - This generates a unique bingo card for you
   - You can only get one card per game
3. **Check your card**: `/mycard`
   - View your card anytime during the game
   - Marked numbers are shown with brackets
4. **Win the game**: Type `BINGO` when you complete the pattern
5. **Check status**: `/status` - See game progress

### For Multi-Group Tournaments
1. **Admin starts tournament**: `/starttournament [classic|dual_action] [pattern]`
   - Example: `/starttournament dual_action blackout`
2. **Join tournament**: `/jointournament`
   - Get your tournament card
   - Compete against players from all groups
3. **Check your card**: `/tournamentcard`
4. **Win tournament**: Type `TOURNAMENT BINGO` when you complete the pattern
5. **Check status**: `/tournamentstatus` - See tournament progress

## Commands

### Player Commands
- `/start` - Show help and available commands
- `/getcard` - Get your card for group game
- `/mycard` - View your current card
- `/status` - Check group game status
- `/jointournament` - Join the daily tournament
- `/tournamentcard` - View your tournament card
- `/tournamentstatus` - Check tournament status

### Admin Commands
- `/startgame [type] [pattern]` - Start a group game
- `/starttournament [type] [pattern]` - Start multi-group tournament
- `/approvegroup` - Approve current group for games
- `/unapprovegroup` - Remove group approval
- `/listgroups` - List all approved groups

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

## Deployed on Render
FREE FOREVER
