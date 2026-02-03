# Quick Start Scripts

These scripts help you quickly set up and launch the Bingo Bot.

## Linux/macOS

### First Time Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your credentials
nano .env  # or use your favorite editor

# 3. Run the start script
./start.sh
```

### Subsequent Launches

```bash
./start.sh
```

## Windows

### First Time Setup

```cmd
# 1. Copy environment template
copy .env.example .env

# 2. Edit .env and add your credentials
notepad .env

# 3. Set environment variables (in Command Prompt)
set BOT_TOKEN=your_token_here
set ADMIN_ID=your_id_here

# 4. Run the start script
start.bat
```

### Subsequent Launches

```cmd
# Set environment variables first
set BOT_TOKEN=your_token_here
set ADMIN_ID=your_id_here

# Then run the script
start.bat
```

## What the Scripts Do

1. ✓ Check Python installation
2. ✓ Create virtual environment (if not exists)
3. ✓ Activate virtual environment
4. ✓ Install/update dependencies
5. ✓ Verify configuration
6. ✓ Start the bot

## Manual Setup

If you prefer to set up manually, see [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) for detailed instructions.

## Troubleshooting

### "Permission denied" on Linux/macOS

```bash
chmod +x start.sh
```

### Scripts don't work

Follow the manual setup instructions in [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md).
