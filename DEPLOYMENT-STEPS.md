# 🚀 Deployment Steps — Tele-Promptr Codex Node

**Step-by-step deployment guide for immediate execution.**

---

## Prerequisites Check

```bash
# Verify Docker is installed
docker --version

# Verify Docker Compose is installed
docker-compose --version

# Should see version numbers for both
```

---

## Step 1: Get Telegram Bot Token

1. Open Telegram app
2. Search for `@BotFather`
3. Start conversation and send: `/newbot`
4. Choose bot name (e.g., "My Codex Bot")
5. Choose username (e.g., "mycodexbot")
6. **Copy the token** — looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

---

## Step 2: Configure Environment

```bash
# Create .env from template
cp .env.example .env

# Edit the file
nano .env
# OR
vim .env
# OR
code .env  # if using VS Code
```

**Add your token:**
```
TELEGRAM_TOKEN=YOUR_TOKEN_FROM_BOTFATHER
N8N_PASSWORD=choose_a_secure_password
```

Save and exit.

---

## Step 3: Deploy All Services

```bash
# Start everything in detached mode
docker-compose up -d

# This will:
# 1. Pull required images (first time only)
# 2. Build bot container
# 3. Start Postgres with pgvector
# 4. Start Redis
# 5. Start n8n
# 6. Start bot worker
```

**Expected output:**
```
Creating network "workspace_default" with the default driver
Creating volume "workspace_pgdata" with default driver
Creating volume "workspace_redisdata" with default driver
Creating volume "workspace_n8ndata" with default driver
Creating codex_postgres ... done
Creating codex_redis    ... done
Creating codex_n8n      ... done
Creating codex_bot      ... done
```

---

## Step 4: Verify Services

```bash
# Check all containers are running
docker-compose ps

# Should show all services as "Up" with healthy status
```

Expected:
```
NAME              STATUS          PORTS
codex_bot         Up              
codex_n8n         Up              0.0.0.0:5678->5678/tcp
codex_postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
codex_redis       Up (healthy)    0.0.0.0:6379->6379/tcp
```

---

## Step 5: Watch Logs (Optional)

```bash
# Watch all logs
docker-compose logs -f

# Watch only bot logs
docker-compose logs -f bot

# Stop watching with Ctrl+C
```

Look for:
```
INFO - ▛//▞▞ ⟦⎊⟧ :: CODEX.BOT.STARTING ⫸
INFO - Database and Redis connected. Bot is ready.
INFO - :: ∎
```

---

## Step 6: Test the Bot

1. Open Telegram
2. Search for your bot username
3. Start conversation
4. Send: `/start`

**Expected response:**
```
▛//▞▞ ⟦⎊⟧ :: CODEX.AWAKENED ⫸

Welcome to your Memory Codex Node.

RITUAL.GUARD
• Begin each prompt with a banner (first line)
• End with seal: :: ∎
• Only sealed messages persist to memory

...
```

---

## Step 7: Send Sealed Message

Send this test message:

```
My First Codex Memory
Today I deployed my personal memory system.
It uses Postgres, Redis, and Telegram.
:: ∎
```

**Expected response:**
```
Banner: My First Codex Memory
Seal: Verified ∎
Status: Memory persisted.
:: ∎
```

---

## Step 8: Check Statistics

Send: `/stats`

**Expected response:**
```
▛//▞▞ Your Memory Statistics ⫸

Events logged: 2
Facts stored: 0
Memory chunks: 0
Last sealed: 2025-10-04 12:34:56

:: ∎
```

---

## Step 9: Test Search

Send: `/recall memory`

Should return your first sealed message!

---

## Step 10: Access n8n (Optional)

1. Open browser: http://localhost:5678
2. Login with credentials from .env file
3. Click "Import from File"
4. Select `/workspace/n8n_flow.json`
5. Configure credentials:
   - Telegram Bot API: Your token
   - Postgres Codex: `postgres://codex:changeme@postgres:5432/codexdb`
6. Activate workflow

---

## Step 11: Verify Database

```bash
# Connect to database
docker exec -it codex_postgres psql -U codex -d codexdb

# Run queries
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM user_facts;
SELECT COUNT(*) FROM memory_chunks;

# View recent events
SELECT id, ts, banner, seal FROM events ORDER BY ts DESC LIMIT 5;

# Exit
\q
```

---

## 🎉 Success!

Your Telegram Codex Memory Node is now running!

**What you have:**
- ✅ Telegram bot responding to commands
- ✅ Postgres database with pgvector
- ✅ Redis cache for sessions
- ✅ n8n for workflows
- ✅ Banner + seal parsing
- ✅ Memory persistence

---

## 📝 Daily Usage

**Commands:**
- `/start` — Show welcome
- `/help` — Show help
- `/stats` — View statistics
- `/recall [query]` — Search memories

**Message format:**
```
Banner (first line)
Content here...
Multiple lines supported.
:: ∎
```

**Only sealed messages persist!**

---

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (DESTRUCTIVE - deletes all data)
docker-compose down -v
```

---

## 🔄 Restarting Services

```bash
# Restart everything
docker-compose restart

# Restart specific service
docker-compose restart bot
```

---

## 🐛 Troubleshooting

### Bot not responding

```bash
# Check if running
docker-compose ps bot

# View logs
docker-compose logs bot

# Restart bot
docker-compose restart bot
```

### Database errors

```bash
# Check Postgres health
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Test connection
docker exec -it codex_postgres pg_isready -U codex -d codexdb
```

### Redis errors

```bash
# Check Redis
docker-compose ps redis

# Test connection
docker exec -it codex_redis redis-cli PING
```

---

## 📊 Monitoring

**View resource usage:**
```bash
docker stats
```

**Check disk usage:**
```bash
docker system df
```

**View networks:**
```bash
docker network ls
```

---

## 💾 Backup

```bash
# Backup Postgres
docker exec codex_postgres pg_dump -U codex -d codexdb > backup-$(date +%Y%m%d).sql

# Backup Redis
docker exec codex_redis redis-cli SAVE
docker cp codex_redis:/data/dump.rdb redis-backup-$(date +%Y%m%d).rdb
```

---

## 🔐 Security

**Before exposing to internet:**

1. Change passwords in .env:
   - POSTGRES_PASSWORD
   - N8N_PASSWORD

2. Restrict port exposure in docker-compose.yml:
   - Remove or comment out Postgres port mapping
   - Remove or comment out Redis port mapping
   - Use reverse proxy for n8n

3. Enable SSL/TLS

4. Set up firewall rules

---

## 📚 Next Steps

- Read full documentation: `TELE-PROMPTR-SETUP.md`
- Customize bot commands
- Add embedding generation
- Set up automated backups
- Configure monitoring
- Deploy to production server

---

**▛//▞▞ Deployment Complete. Codex Active. Memory Persists. ⫸**

:: ∎
