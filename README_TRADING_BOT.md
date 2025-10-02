## Trading Mission Commander Bot

Purpose-built Telegram bot to lock in your daily trading mission, parse Phames analysis, and keep you disciplined with a badass tone.

### Features
- Locks the day's bias and refuses mid-day changes
- Parses Phames analysis text to infer bias and 4H conditions
- Enforces rule: if 4H is long, do not short
- Daily check-in message and day reset
- Lightweight portfolio tracking and USD valuation via CoinGecko

### Setup
1. Install dependencies:
```bash
make install
```
2. Create `.env` (or run):
```bash
make env-example
```
3. Edit `.env` with real values:
- TELEGRAM_BOT_TOKEN
- PHAMES_CHAT_ID (Telegram chat id where Phames posts)
- MISSION_CHAT_ID (thread/group where you want the bot to speak)
- PHAMES_USERNAME (optional)
- AUTO_LOCK=1 to auto-lock mission on first analysis seen

### Run
```bash
make run-bot
```

### Commands
- /start, /help – show help
- /goal <text> – set mission plan text (infers bias)
- /lock – lock the mission for the day
- /status – show current mission state
- /pos <SYMBOL> <AMOUNT> – set a holding
- /value – show total portfolio value (USD)

### Notes
- State is stored in `data/mission_state.json`
- The bot listens to regular messages to detect Phames analysis and enforce rules
