@echo off
REM Quick Start Script for Bingo Bot (Windows)
REM This script helps you set up and launch the bot quickly

echo ========================================
echo  Bingo Bot - Quick Start Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt --upgrade
echo [OK] Dependencies installed
echo.

REM Check for .env file
if not exist ".env" (
    echo [WARNING] No .env file found!
    echo.
    echo Please create a .env file with your configuration:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env and add your BOT_TOKEN and ADMIN_ID
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

REM Note: Windows batch doesn't easily source .env files
REM Users should set environment variables manually or use PowerShell

echo ========================================
echo  Starting Bingo Bot...
echo ========================================
echo.
echo Press Ctrl+C to stop the bot
echo.

REM Start the bot
python bot.py

pause
