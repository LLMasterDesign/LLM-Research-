# Τ{Raven} ≔ Telegram Command Station

Raven is a Telegram bot that acts as a command station to your coding copilot. It can route messages to an OpenAI backend, an n8n webhook, or a generic relay.

## Quick start (local, polling)

1. Copy `.env.example` to `.env` and fill in values:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY` (if using OpenAI)
   - optional: `ALLOWED_USER_IDS` comma-separated (restrict access)
2. Create Python venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the bot:

```bash
python -m raven.bot
```

## Docker

```bash
docker compose up --build -d
```

## Webhook mode

Set in `.env`:

```
USE_WEBHOOK=true
WEBHOOK_URL=https://your.domain/raven
PORT=8080
```

Expose port `8080` and ensure Telegram can reach your webhook URL.

## Commands

- `/start` — show help
- `/backend openai|n8n|relay` — set or show backend
- `/clear` — clear conversation history

## Backends

- **OpenAI**: Uses Chat Completions with model `OPENAI_MODEL` and `SYSTEM_PROMPT`.
- **n8n**: POSTs JSON `{chat_id, history, message}` to `N8N_WEBHOOK_URL`, expects `{ reply: string }`.
- **Relay**: POSTs to `RELAY_URL` with the same payload.

## Persistence

Conversation history is stored in SQLite at `DB_PATH` using `aiosqlite`.
