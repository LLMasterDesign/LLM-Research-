# ⚡ Quick Start — Telegram Codex Memory Node

Get your Codex running in 5 minutes.

---

## 1️⃣ Get Telegram Bot Token

1. Open Telegram → search `@BotFather`
2. Send: `/newbot`
3. Follow prompts, copy your token

---

## 2️⃣ Configure

```bash
# Create environment file
cp .env.example .env

# Edit and add your token
nano .env
```

Paste your token:
```
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## 3️⃣ Launch

```bash
docker-compose up -d
```

Wait 30 seconds for initialization.

---

## 4️⃣ Test

Open Telegram, find your bot, send:

```
/start
```

Then send a sealed message:

```
My First Memory
This is a test of the Codex system.
:: ∎
```

You should receive confirmation! ✅

---

## 5️⃣ View Stats

```
/stats
```

---

## 📚 Next Steps

- Read full docs: `TELE-PROMPTR-SETUP.md`
- Import n8n workflow: http://localhost:5678
- Query database: `docker exec -it codex_postgres psql -U codex -d codexdb`

---

**Your Memory Codex is live. :: ∎**
