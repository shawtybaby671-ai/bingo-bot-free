# Player Data Logging - Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLAYER DATA LOGGING SYSTEM                        │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   PLAYER     │
                    │  (User ID)   │
                    └──────┬───────┘
                           │
                           │ 1. DMs Bot with
                           │    Registration Link
                           ▼
                    ┌──────────────┐
                    │   BOT        │
                    │  Processes   │
                    │  Request     │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        │ 2a. Save to     │ 2b. Log to      │ 2c. Send to
        │     File         │      Group       │     Admin
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  JSON FILE   │   │   PRIVATE    │   │    ADMIN     │
│              │   │    GROUP     │   │   (Telegram) │
│ player_data/ │   │  (Optional)  │   │              │
│  └─ player_  │   │              │   │  Approval    │
│     12345_   │   │ #user_12345  │   │  Buttons     │
│     reg_501  │   │ #reg_501     │   │  ✅ ❌      │
│     .json    │   │ #pending     │   └──────┬───────┘
└──────────────┘   └──────────────┘          │
                                              │ 3. Admin
                                              │    Decides
                                              ▼
                                       ┌──────────────┐
                                       │   ADMIN      │
                                       │  Approves/   │
                                       │   Rejects    │
                                       └──────┬───────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                        │ 4a. Update File    │ 4b. Log to Group   │ 4c. Notify Player
                        ▼                     ▼                     ▼
                ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
                │  JSON FILE   │      │   PRIVATE    │      │   PLAYER     │
                │              │      │    GROUP     │      │  (Telegram)  │
                │ + admin_     │      │              │      │              │
                │   approval   │      │ #approved    │      │ ✅ Approved! │
                │   message    │      │ #rejected    │      │              │
                └──────────────┘      └──────────────┘      └──────────────┘
```

## Storage Details

### File System Structure
```
project_root/
├── player_data/                     # Created automatically
│   ├── player_12345_reg_501.json  # DM conversation for reg 501
│   ├── player_12345_reg_502.json  # DM conversation for reg 502
│   ├── player_12345_profile.json  # Profile snapshot with all regs
│   ├── player_67890_reg_503.json  # Another player's conversation
│   └── player_67890_profile.json  # Another player's profile
└── bot.py
```

### JSON File Format

**Conversation File** (`player_{user_id}_reg_{registration_id}.json`):
```json
{
  "user_id": 12345,
  "registration_id": 501,
  "created_at": "2026-02-03T10:00:00.000Z",
  "last_updated": "2026-02-03T10:15:00.000Z",
  "messages": [
    {
      "timestamp": "2026-02-03T10:00:00.000Z",
      "type": "registration_request",
      "data": {
        "registration_id": 501,
        "game_id": 1,
        "cards_requested": 3,
        "points_paid": 30,
        "game_date": "2026-02-10",
        "game_time": "18:00",
        "game_type": "classic",
        "pattern": "single_line",
        "status": "pending"
      }
    },
    {
      "timestamp": "2026-02-03T10:15:00.000Z",
      "type": "admin_approval",
      "data": {
        "approved": true,
        "admin_id": 123456,
        "admin_name": "AdminName"
      }
    }
  ]
}
```

**Profile File** (`player_{user_id}_profile.json`):
```json
{
  "user_id": 12345,
  "username": "JohnDoe",
  "created_at": "2026-02-03T09:00:00.000Z",
  "last_updated": "2026-02-03T10:15:00.000Z",
  "registrations": [
    {
      "timestamp": "2026-02-03T10:00:00.000Z",
      "registration_id": 501,
      "game_id": 1,
      "cards_requested": 3,
      "points_paid": 30,
      "status": "confirmed",
      "game_date": "2026-02-10",
      "game_time": "18:00",
      "game_type": "classic",
      "pattern": "single_line"
    }
  ]
}
```

## Private Group Message Flow

### When Player DMs Bot

```
┌────────────────────────────────────────────────────┐
│  📝 *New Registration Request*                     │
│                                                     │
│  #user_12345 #reg_501 #pending                    │
│                                                     │
│  👤 Player: JohnDoe                                │
│  🆔 User ID: 12345                                 │
│  🎮 Game ID: #1                                    │
│  📆 Game Date: 2026-02-10                          │
│  🕐 Game Time: 18:00                               │
│  🎴 Cards Requested: 3                             │
│  💎 Points Required: 30                            │
│  🏆 Type: classic - single_line                    │
│  📊 Status: pending                                │
│  🕐 Timestamp: 2026-02-03 10:00:00                │
└────────────────────────────────────────────────────┘
```

### When Admin Approves

```
┌────────────────────────────────────────────────────┐
│  ✅ *Registration Approved*                        │
│                                                     │
│  #user_12345 #reg_501 #approved                   │
│                                                     │
│  👤 Player: JohnDoe                                │
│  👮 Admin: AdminName                               │
│  📋 Registration ID: #501                          │
│  🕐 Timestamp: 2026-02-03 10:15:00                │
└────────────────────────────────────────────────────┘
```

### When Admin Rejects

```
┌────────────────────────────────────────────────────┐
│  ❌ *Registration Rejected*                        │
│                                                     │
│  #user_12345 #reg_501 #rejected                   │
│                                                     │
│  👤 Player: JohnDoe                                │
│  👮 Admin: AdminName                               │
│  📋 Registration ID: #501                          │
│  🕐 Timestamp: 2026-02-03 10:15:00                │
└────────────────────────────────────────────────────┘
```

## Admin Command Flow

### `/loguser <user_id>` Command

```
Admin Types:        Bot Responds:          Bot Sends to Group:
/loguser 12345  →   Querying DB...    →   👤 *Player Profile Update*
                    Found player!          #user_12345 #profile
                    Logging...             🎭 Username: JohnDoe
                    ✅ Done!              💎 Points: 85
                                           ...
```

### `/logreg <registration_id>` Command

```
Admin Types:        Bot Responds:          Bot Sends to Group:
/logreg 501     →   Querying DB...    →   📝 *New Registration Request*
                    Found reg!             #user_12345 #reg_501
                    Logging...             👤 Player: JohnDoe
                    ✅ Done!              🎮 Game ID: #1
                                           ...
```

### `/logdm <user_id> <registration_id>` Command

```
Admin Types:        Bot Responds:          Bot Sends to Group:
/logdm 12345 501 → Reading file...    →   📋 *DM History*
                    Found data!            #user_12345 #reg_501
                    Logging...             💬 Messages: 2
                    ✅ Done!              • registration_request
                                           • admin_approval
```

## Hashtag Search System

### Search Capabilities

**By User**:
```
Search: #user_12345
Result: All messages for user 12345
        - Registration requests
        - Approvals/rejections
        - Profile updates
        - DM interactions
```

**By Registration**:
```
Search: #reg_501
Result: All messages for registration 501
        - Initial request
        - Admin decision
        - Status updates
```

**By Status**:
```
Search: #approved
Result: All approved registrations

Search: #rejected
Result: All rejected registrations

Search: #pending
Result: All pending registrations
```

**Combined Search**:
```
Search: #user_12345 #approved
Result: All approved registrations for user 12345

Search: #reg_501 #approved
Result: Approval message for registration 501
```

## Data Flow Summary

1. **Player Action** → DM bot with registration link
2. **Bot Processes** → Validates request, gets details
3. **Dual Storage**:
   - Save to JSON file (always)
   - Log to private group (if configured)
4. **Admin Notified** → Receives approval request
5. **Admin Decides** → Approves or rejects
6. **Update Storage**:
   - Update JSON file (always)
   - Log decision to group (if configured)
7. **Player Notified** → Receives decision
8. **Audit Trail** → Complete history in files and group

## Benefits Visualization

```
┌─────────────────────┐
│   FILE STORAGE      │
├─────────────────────┤
│ ✓ Always enabled    │
│ ✓ Programmatic      │
│ ✓ Structured JSON   │
│ ✓ Local backup      │
│ ✓ No dependencies   │
└─────────────────────┘
         +
┌─────────────────────┐
│  PRIVATE GROUP      │
├─────────────────────┤
│ ✓ Human readable    │
│ ✓ Telegram search   │
│ ✓ Easy review       │
│ ✓ Collaborative     │
│ ✓ Real-time         │
└─────────────────────┘
         =
┌─────────────────────┐
│  COMPLETE AUDIT     │
│      TRAIL          │
├─────────────────────┤
│ ✓ Dual backup      │
│ ✓ Multiple access   │
│ ✓ Easy search       │
│ ✓ Full history      │
│ ✓ Compliance ready  │
└─────────────────────┘
```
