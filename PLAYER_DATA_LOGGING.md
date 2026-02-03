# Player Data Logging - Setup and Usage Guide

## Overview

The bingo bot now includes comprehensive player data logging with two storage methods:
1. **File-based storage** - Automatic, always enabled
2. **Private group logging** - Optional, requires setup

## 📁 File-Based Storage

### Automatic Operation
- **Location**: `player_data/` directory
- **Format**: JSON files
- **Enabled**: Always, no configuration needed

### Files Created

1. **DM Conversation Files**
   - Pattern: `player_{user_id}_reg_{registration_id}.json`
   - Contains: All messages in the registration workflow
   - Example: `player_12345_reg_501.json`

2. **Profile Snapshot Files**
   - Pattern: `player_{user_id}_profile.json`
   - Contains: Player registration history
   - Example: `player_12345_profile.json`

### When Files Are Created

- When player DMs bot with registration link
- When admin approves/rejects registration
- When player profile is accessed

## 💬 Private Group Logging

### Setup Instructions

#### Step 1: Create Private Group
1. In Telegram, create a new group
2. Make it private (not public)
3. Give it a name like "Bingo Bot Logs" or "Player Data"

#### Step 2: Add Bot as Admin
1. Add your bot to the group
2. Promote bot to administrator
3. Grant these permissions:
   - Post messages
   - Delete messages (optional)
   - Pin messages (optional)

#### Step 3: Get Group Chat ID
There are several ways to get the chat ID:

**Method 1: Forward Message**
1. Forward any message from the group to @userinfobot
2. Bot will reply with the chat ID
3. Format: `-1001234567890` (negative number for groups)

**Method 2: Use Bot**
1. Add @RawDataBot to your group temporarily
2. It will show the chat ID
3. Remove the bot after getting the ID

**Method 3: Through API**
1. Send a message in the group
2. Use `getUpdates` API endpoint
3. Look for `chat.id` in the response

#### Step 4: Set Environment Variable

**On Local Development**:
```bash
export PLAYER_DATA_GROUP_ID=-1001234567890
```

**On Render/Heroku**:
1. Go to your app settings
2. Find "Environment Variables" section
3. Add new variable:
   - Key: `PLAYER_DATA_GROUP_ID`
   - Value: `-1001234567890` (your actual chat ID)

**Using .env file**:
```
PLAYER_DATA_GROUP_ID=-1001234567890
```

#### Step 5: Restart Bot
- Restart the bot to load the new environment variable
- Check bot logs for confirmation

### What Gets Logged

#### Automatic Logging

**1. Registration Requests**
- When player DMs bot
- Includes all registration details
- Tagged: `#user_{id}`, `#reg_{id}`, `#pending`

**2. Admin Approvals**
- When admin approves registration
- Includes admin name and timestamp
- Tagged: `#user_{id}`, `#reg_{id}`, `#approved`

**3. Admin Rejections**
- When admin rejects registration
- Includes admin name and timestamp
- Tagged: `#user_{id}`, `#reg_{id}`, `#rejected`

**4. DM Interactions**
- Key player interactions
- Tagged: `#user_{id}`, `#dm`

### Manual Logging Commands

Use these commands **in the private group** or in DM with bot:

#### `/loguser <user_id>`
Logs current player profile to the group.

**Example**:
```
/loguser 12345
```

**Output**:
```
👤 *Player Profile Update*

#user_12345 #profile

🎭 Username: JohnDoe
🆔 User ID: 12345
💎 Points: 85
🎴 Cards Owned: 2
🕐 Timestamp: 2026-02-03 10:30:00
```

#### `/logreg <registration_id>`
Logs registration details to the group.

**Example**:
```
/logreg 501
```

**Output**:
```
📝 *New Registration Request*

#user_12345 #reg_501 #approved

👤 Player: JohnDoe
🆔 User ID: 12345
🎮 Game ID: #1
📆 Game Date: 2026-02-10
🕐 Game Time: 18:00
🎴 Cards Requested: 3
💎 Points Required: 30
🏆 Type: classic - single_line
📊 Status: confirmed
🕐 Timestamp: 2026-02-03 10:30:00
```

#### `/logdm <user_id> <registration_id>`
Logs DM conversation history from file to the group.

**Example**:
```
/logdm 12345 501
```

**Output**:
```
📋 *DM History*

#user_12345 #reg_501 #dm_history

🆔 User ID: 12345
📋 Registration ID: #501
📅 Created: 2026-02-03T10:00:00
🔄 Last Updated: 2026-02-03T10:15:00
💬 Messages: 2

• registration_request: 2026-02-03T10:00:00
• admin_approval: 2026-02-03T10:15:00
```

## 🔍 Searching Messages

### Using Hashtags

In the private group, use Telegram's search feature with hashtags:

**Search by User**:
```
#user_12345
```
Shows all messages related to user ID 12345

**Search by Registration**:
```
#reg_501
```
Shows all messages related to registration #501

**Search by Status**:
```
#approved
#rejected
#pending
```
Shows all registrations with that status

**Combined Search**:
```
#user_12345 #approved
```
Shows all approved registrations for user 12345

### Search Tips

1. **Click on hashtag** in any message to see all messages with that tag
2. **Use search bar** at top of chat
3. **Filter by date** using Telegram's date filter
4. **Pin important messages** for quick access

## 📊 Data Analysis

### Using Files

**Read all files**:
```python
import os
import json

for filename in os.listdir('player_data'):
    if filename.endswith('.json'):
        with open(f'player_data/{filename}') as f:
            data = json.load(f)
            # Process data
```

**Find specific user**:
```python
user_id = 12345
files = [f for f in os.listdir('player_data') 
         if f.startswith(f'player_{user_id}_')]
```

### Using Private Group

1. **Export chat history** from Telegram
2. **Parse messages** for data analysis
3. **Use bot API** to programmatically access messages

## 🔒 Security Considerations

### File Storage
- `player_data/` is in `.gitignore`
- Never commit player data to repository
- Backup directory regularly
- Restrict file system permissions

### Private Group
- Keep group private (not public)
- Only add trusted admins
- Regularly review group members
- Enable group history for new members: OFF

## 🐛 Troubleshooting

### "Private group logging not configured"
**Problem**: Environment variable not set
**Solution**: Set `PLAYER_DATA_GROUP_ID` and restart bot

### "Error logging to private group"
**Problem**: Bot not admin or wrong chat ID
**Solution**: 
1. Check bot is admin in group
2. Verify chat ID is correct (negative number)
3. Check bot has posting permissions

### Files not being created
**Problem**: Directory permissions
**Solution**: 
1. Check `player_data/` directory exists
2. Check write permissions
3. Check disk space

### Messages not appearing in group
**Problem**: Bot not properly configured
**Solution**:
1. Verify bot is administrator
2. Check it has "Post messages" permission
3. Try sending test message: `/loguser <any_user_id>`

## 📈 Best Practices

1. **Regular Backups**: Backup `player_data/` directory daily
2. **Archive Old Logs**: Move old data to archive after X months
3. **Monitor Storage**: Check disk usage regularly
4. **Review Access**: Audit who has access to private group
5. **Test Logging**: Periodically test manual logging commands
6. **Document Changes**: Note any configuration changes

## 🎯 Use Cases

### For Admins

**Daily Tasks**:
- Review pending registrations in private group
- Search player history before approving
- Check for duplicate registrations

**Weekly Tasks**:
- Analyze registration patterns
- Review approval/rejection rates
- Backup player data files

**Monthly Tasks**:
- Archive old messages
- Review storage usage
- Update documentation

### For Developers

**Debugging**:
- Review DM interaction logs
- Check approval workflow
- Trace user actions

**Analytics**:
- Extract data from JSON files
- Generate reports
- Identify trends

**Auditing**:
- Verify all actions are logged
- Check data integrity
- Review error logs

## 📚 Additional Resources

- **Bot Code**: `bot.py` (lines 280-460 for logging functions)
- **Tests**: `test_player_data.py`
- **Documentation**: This file
- **README**: Main project README with feature overview
