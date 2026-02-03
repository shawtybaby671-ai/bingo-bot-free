#!/bin/bash
# Quick Start Script for Bingo Bot
# This script helps you set up and launch the bot quickly

set -e

echo "🎰 Bingo Bot - Quick Start Script"
echo "=================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt --upgrade
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo ""
    echo "Please create a .env file with your configuration:"
    echo "  1. Copy .env.example to .env:"
    echo "     cp .env.example .env"
    echo "  2. Edit .env and add your BOT_TOKEN and ADMIN_ID"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required variables
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    echo ""
    echo "❌ BOT_TOKEN not set in .env file!"
    echo "   Get your token from @BotFather on Telegram"
    exit 1
fi

if [ -z "$ADMIN_ID" ] || [ "$ADMIN_ID" = "your_telegram_user_id" ]; then
    echo ""
    echo "❌ ADMIN_ID not set in .env file!"
    echo "   Get your user ID from @userinfobot on Telegram"
    exit 1
fi

echo ""
echo "✓ Configuration loaded"
echo ""
echo "=================================="
echo "🚀 Starting Bingo Bot..."
echo "=================================="
echo ""
echo "Bot Token: ${BOT_TOKEN:0:10}...${BOT_TOKEN: -5}"
echo "Admin ID: $ADMIN_ID"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Start the bot
python3 bot.py
