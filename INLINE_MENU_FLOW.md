# 🎮 Inline Menu System - User Flow Documentation

## Overview
This document describes the complete user flow for the inline menu system implemented in the bingo bot.

## 1. Main Menu
**Trigger:** `/start` or `/menu`

**Display:**
```
🎰 Welcome to Bingo Bot, [Username]!

Choose an option from the menu below:

[👤 Player Profile] [📋 Commands]
[📖 Rules] [🎮 Request Game Type]
[📅 Game Schedule] [🎯 Join a Game]
```

## 2. Player Profile
**Navigation:** Main Menu → 👤 Player Profile

**Display:**
```
👤 Player Profile

🎭 Name: TestUser
💎 Points: 100
🎴 Cards Owned: 0
🆔 ID: 12345

[⬅️ Back to Menu]
```

## 3. Commands List
**Navigation:** Main Menu → 📋 Commands

**Display:**
```
📋 Available Commands:

• /start - Show main menu
• /menu - Show main menu
• /commands - Commands list
• /profile - Your profile
• /schedule - Game schedule

[⬅️ Back to Menu]
```

## 4. Rules
**Navigation:** Main Menu → 📖 Rules

**Display:**
```
📖 Bingo Game Rules

How to Play:
1. Join a scheduled game from the Game Schedule menu
2. Select number of cards you want (costs points per card)
3. Approve your purchase and DM the bot
4. Admin will approve your request
5. You'll be added to the game and receive your cards

Card Types:
• Classic: Single number per cell
• Dual Action: Two numbers per cell

Winning Patterns:
• Single Line
• Four Corners
• Blackout (Full Card)
• Letter X
• Postage Stamp

[⬅️ Back to Menu]
```

## 5. Request Game Type
**Navigation:** Main Menu → 🎮 Request Game Type

**Display:**
```
🎮 Request Game Type

Select the type of game you'd like to request:

[Classic] [Dual Action]

[⬅️ Back to Menu]
```

**After Selection:**
```
✅ Request Sent!

You've requested a classic game.
The admin has been notified.

[⬅️ Back to Menu]
```

## 6. Game Schedule
**Navigation:** Main Menu → 📅 Game Schedule

**Display:**
```
📅 Upcoming Games

Game #1
📆 Date: 2026-02-10
🕐 Time: 18:00
🎮 Type: classic
🏆 Pattern: single_line
💎 Entry: 10 points per card
👥 Max Players: 50
─────────────

[⬅️ Back to Menu]
```

## 7. Join a Game
**Navigation:** Main Menu → 🎯 Join a Game

**Step 1: Game Selection**
```
🎯 Select a Game to Join

Click on a game to join:

[Game #1 - 2026-02-10 18:00]
[Game #2 - 2026-02-15 20:00]

[⬅️ Back to Menu]
```

**Step 2: Card Selection**
```
🎯 Joining Game #1

📆 Date: 2026-02-10
🕐 Time: 18:00
🎮 Type: classic
🏆 Pattern: single_line
💎 Cost: 10 points per card

How many cards would you like?

[1 Card] [2 Cards] [3 Cards]
[4 Cards] [5 Cards] [6 Cards]

[⬅️ Back]
```

**Step 3: Confirmation**
```
🎴 Confirm Purchase

Cards Requested: 3
Points Required: 30
Your Points: 100

✅ You have enough points!

Do you want to proceed?

[✅ Approve] [❌ Cancel]
```

**Step 4: DM Instructions**
```
✅ Request Submitted!

Registration ID: #42
Game ID: #1
Cards: 3

📩 Next Steps:
1. Click the button below to start a DM with the bot
2. Click 'Start' in the DM
3. Wait for admin approval
4. Once approved, your points will be deducted and you'll be added to the game!

[💬 Open DM with Bot]

[⬅️ Back to Menu]
```

## 8. DM Workflow

**Player DMs Bot:**
User clicks the deep link button and is redirected to DM with bot.
Bot automatically processes the registration link.

**Bot Response to Player:**
```
✅ Request Sent to Admin!

Registration ID: #42
Game: #1 on 2026-02-10
Cards: 3

⏳ Please wait for admin approval.
You'll be notified once the decision is made.
```

**Admin Receives:**
```
🔔 New Registration Request

👤 Player: TestUser (ID: 12345)
🎮 Game #1
📆 2026-02-10 18:00
🎴 Cards: 3
💎 Points: 30
🏆 Type: classic - single_line

Do you approve this registration?

[✅ Approve] [❌ Reject]
```

## 9. Admin Approval

**If Admin Approves:**

**Admin Sees:**
```
[Original request text]

✅ APPROVED
```

**Player Receives:**
```
🎉 Registration Approved!

Game #1 on 2026-02-10
Cards: 3
Points Deducted: 30

You've been added to the card holder list!
You'll receive your cards when the game starts.
```

**If Admin Rejects:**

**Admin Sees:**
```
[Original request text]

❌ REJECTED
```

**Player Receives:**
```
❌ Registration Rejected

Game #1 on 2026-02-10
Your registration was not approved.

No points were deducted.
You can try joining another game.
```

## Key Features

### Inline Buttons
- No typing required for navigation
- Fast and intuitive interface
- Visual feedback on selections

### Points System
- Balance shown before purchase
- Validation prevents overspending
- Deduction only after approval

### Deep Linking
- Seamless transition to DM
- Registration ID preserved in link
- Auto-processing of registration

### Admin Control
- Review all registration details
- Approve/reject with one click
- Automatic points handling

### Status Tracking
- Pending → Approved/Rejected
- Player notified at each step
- Transparent workflow

## Commands Summary

### Player Commands
- `/start` or `/menu` - Main menu
- `/commands` - Commands list
- `/profile` - View profile
- `/schedule` - View schedule

### Admin Commands
- `/schedulegame <date> <time> <type> <pattern> [cost]` - Schedule game
- `/approvegroup` - Approve group
- `/listgroups` - List groups

## Error Handling

### Insufficient Points
```
🎴 Confirm Purchase

Cards Requested: 10
Points Required: 100
Your Points: 50

❌ Insufficient Points!
You need 50 more points.

[⬅️ Back]
```

### Invalid Registration
```
❌ This registration doesn't belong to you!
```

### Game Not Found
```
❌ Game not found!
```

## Navigation Flow Chart

```
                    /start or /menu
                          |
                     [Main Menu]
                          |
        +-----------------+------------------+
        |                 |                  |
   [Profile]          [Rules]          [Join Game]
        |                 |                  |
   [Back to Main]   [Back to Main]     [Game List]
                                             |
                                       [Card Count]
                                             |
                                       [Confirmation]
                                             |
                                        [DM Button]
                                             |
                                      [DM with Bot]
                                             |
                                    [Admin Notification]
                                             |
                                    [Admin Approval]
                                             |
                                    [Player Notification]
```

## Technical Implementation

### Database Tables
1. **player_profiles**: User data and points
2. **scheduled_games**: Game details
3. **game_registrations**: Registration tracking

### Callback Data Patterns
- `menu_*` - Menu navigation
- `join_game_*` - Game selection
- `cards_*_*` - Card count selection
- `approve_*_*` - Purchase confirmation
- `admin_approve_*` - Admin approval
- `admin_reject_*` - Admin rejection

### Deep Link Format
```
https://t.me/BotUsername?start=reg_{registration_id}
```

This format preserves the registration ID when the user clicks the button and starts a DM with the bot.
