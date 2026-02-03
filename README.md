# 🎰 Free Bingo Bot

Simple Telegram bingo bot with a background game loop and optional webhook mode.

## Commands
- `/start` - Welcome
- `/startgame` - Start game (Admin)
- `/status` - Game status

## Local setup
1) Install deps:
	- `pip install -r requirements.txt`
2) Set env vars:
	- `BOT_TOKEN` (required)
	- `ADMIN_ID` (required)
	- `USE_WEBHOOK=1` (optional)
3) Run:
	- `python bot.py`

## Runtime modes
- Polling (default): `bot.infinity_polling()`
- Webhook (optional): set `USE_WEBHOOK=1` and ensure Render sets `PORT`

## Deployment (Render)
This repo includes a Render worker definition in [render.yaml](render.yaml):
- Build: `pip install -r requirements.txt`
- Start: `python bot.py`

Set env vars in Render:
- `BOT_TOKEN`
- `ADMIN_ID`
- `USE_WEBHOOK=1` (if using webhook mode)
- `PORT` (Render provides this automatically)

## Game rules
See [GAME_SOP_AND_LOGIC.md](GAME_SOP_AND_LOGIC.md).
