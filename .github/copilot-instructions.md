## Project overview
- Single-file Python Telegram bot in [bot.py](bot.py) using `pyTelegramBotAPI` with optional Flask webhook mode.
- Core game state is in-memory globals (`game_active`, `called_numbers`, `jackpot`, `current_game_id`) and is reset on `/startgame`.
- A background thread runs `game_loop()` to draw numbers, generate a flashboard image, and send updates.

## Runtime modes
- Polling (default): `bot.infinity_polling()` in [bot.py](bot.py).
- Webhook: set `USE_WEBHOOK=1` to run Flask routes (`/` and `/<BOT_TOKEN>`); used for Render deployments.

## Local workflow
- Install deps with `pip install -r requirements.txt`, then run `python bot.py` (matches [render.yaml](render.yaml)).
- There are no test scripts; manual verification is via `/start`, `/startgame`, and `/status` behavior in [GAME_SOP_AND_LOGIC.md](GAME_SOP_AND_LOGIC.md).

## Commands and handlers
- `/start`, `/startgame`, `/status` handlers are in [bot.py](bot.py) and match the SOP in [GAME_SOP_AND_LOGIC.md](GAME_SOP_AND_LOGIC.md).
- Any message containing “bingo” triggers a random prize reply (`echo()` handler).

## Images and game loop
- `create_board()` draws a 15x5 dot grid (1–75) using Pillow; called numbers are red, others white.
- Every 10 calls in `game_loop()` triggers “HOT NUMBERS” and increments the jackpot by +5.

## Persistence
- SQLite `game.db` is initialized at startup; `games` table exists but is not yet written to.

## Configuration
- Required env vars: `BOT_TOKEN` (or `/etc/secrets/bot-token` on Render), `ADMIN_ID`.
- Optional: `USE_WEBHOOK=1`, `PORT` for Flask.

## Dependency and deploy notes
- Python deps are pinned in [requirements.txt](requirements.txt).
- Render worker config is in [render.yaml](render.yaml) with `python bot.py` as the start command.
