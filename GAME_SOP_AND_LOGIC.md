# Game SOP and Logic

## Purpose
Defines how the Bingo game runs, how commands behave, and how the bot manages state.

## Roles
- **Admin**: The Telegram user whose numeric ID matches `ADMIN_ID`.
- **Players**: Anyone in the chat who interacts with the bot.

## Commands
- `/start`
  - Sends a welcome message and lists available commands.
- `/startgame` (Admin only)
  - Starts a new game loop.
  - Increments `current_game_id`.
  - Increases `jackpot` by 10.
  - Clears `called_numbers`.
- `/status`
  - Reports whether a game is active.
  - If active, shows called count and jackpot.

## Game State (in-memory)
- `game_active`: `True` while a game is running.
- `called_numbers`: List of integers already called (1–75).
- `jackpot`: Integer value that grows during the game.
- `current_game_id`: Integer that increments per new game.

## Game Loop
- Runs in a background thread after `/startgame`.
- While `game_active` and fewer than 75 numbers called:
  - Randomly select a number between 1–75 not yet called.
  - Add to `called_numbers`.
  - Generate a simple flashboard image:
    - 15x5 grid of circles
    - Red circles = called numbers, white = uncalled
  - Send the image to the chat with the called number.
  - Every 10 calls, announce “HOT NUMBERS” and add +5 to `jackpot`.
  - Sleep 3 seconds between calls.
- When complete:
  - Set `game_active = False`.
  - Announce game over.

## “Bingo” Message Handling
- Any message containing the word “bingo” triggers a reply with a random prize amount.

## Persistence
- A local SQLite file `game.db` is created.
- Table `games` exists but is not yet used for writes in current logic.

## Runtime Modes
- **Polling (default)**: `bot.infinity_polling()` when running `python bot.py`.
- **Webhook (optional)**: Enable by setting `USE_WEBHOOK=1` and running the Flask app.

## Environment Variables
- `BOT_TOKEN` (required) or `/etc/secrets/bot-token` on Render
- `ADMIN_ID` (required for admin-only commands)
- `USE_WEBHOOK` (optional; set to `1` to use Flask webhook mode)

## Expected Behavior Checklist
- `/start` responds immediately.
- `/startgame` only works for the admin.
- Called numbers never repeat within a game.
- `jackpot` increases at game start and every 10 calls.
