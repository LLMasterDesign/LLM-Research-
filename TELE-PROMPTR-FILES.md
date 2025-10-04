# ▛//▞▞ ⟦⎊⟧ :: TELE-PROMPTR UPGRADE FILES ⫸

**Research Documentation: Complete File Manifest**

This document catalogs all files created for the Telegram Codex Memory Node deployment.

---

## 📦 Core Infrastructure Files

### `docker-compose.yml`
**Location**: `/workspace/docker-compose.yml`  
**Purpose**: Orchestrates all services (Postgres, Redis, Bot, n8n)  
**Status**: ✅ Ready to deploy

**Services defined:**
- `postgres` — ankane/pgvector with auto-initialization
- `redis` — Redis 7 with persistent volume
- `bot` — Custom Python bot worker
- `n8n` — Workflow orchestration UI

**Features:**
- Health checks for all services
- Automatic seed.sql initialization
- Volume persistence
- Service dependencies

---

### `seed.sql`
**Location**: `/workspace/seed.sql`  
**Purpose**: Database schema initialization with pgvector support  
**Status**: ✅ Drift-locked

**Tables created:**
1. `user_facts` — Persisted facts with confidence scores and seal timestamps
2. `events` — All user interactions (banner + seal tracking)
3. `memory_chunks` — Text storage with vector embeddings (1536 dimensions)

**Indexes:**
- IVFFlat index on embeddings for fast similarity search
- Compound indexes on user_id and timestamps
- Partial index on active facts

**Extensions:**
- pgvector for semantic search capabilities

---

### `n8n_flow.json`
**Location**: `/workspace/n8n_flow.json`  
**Purpose**: Pre-configured n8n workflow for Telegram integration  
**Status**: ✅ Import-ready

**Flow stages:**
1. **Telegram Trigger** — Listens for incoming messages
2. **Extract Banner/Seal** — JavaScript function to parse ritual format
3. **Log Event** — Postgres insert operation
4. **Embed & Store** — Placeholder for embedding generation
5. **Reply to User** — Confirmation message with seal

**Configuration needed:**
- Telegram Bot API credentials
- Postgres connection credentials

---

## 🤖 Bot Application

### `bot/Dockerfile`
**Location**: `/workspace/bot/Dockerfile`  
**Purpose**: Container definition for bot worker  
**Base**: python:3.11-slim

**System dependencies:**
- gcc (for asyncpg compilation)
- postgresql-client (for health checks)

---

### `bot/requirements.txt`
**Location**: `/workspace/bot/requirements.txt`  
**Purpose**: Python dependencies

**Key packages:**
- `aiogram==3.3.0` — Modern async Telegram bot framework
- `asyncpg==0.29.0` — High-performance async Postgres driver
- `redis==5.0.1` — Async Redis client
- `python-dotenv==1.0.0` — Environment configuration
- `psycopg2-binary==2.9.9` — Postgres adapter
- `openai==1.12.0` — For future embedding generation
- `pydantic==2.6.0` — Data validation

---

### `bot/main.py`
**Location**: `/workspace/bot/main.py`  
**Purpose**: Main bot entry point and command handlers  
**Lines**: ~200

**Commands implemented:**
- `/start` — Initialize Codex with welcome message
- `/help` — Show ritual format and commands
- `/stats` — Display user memory statistics
- `/recall [query]` — Search sealed memories

**Features:**
- Banner extraction (first line)
- Seal validation (`:: ∎`)
- Event logging to Postgres
- Redis caching
- HTML-formatted responses

**Handler flow:**
```
Message received
    ↓
Extract banner (line 1)
    ↓
Check for seal (:: ∎)
    ↓
Log to events table
    ↓
Cache in Redis
    ↓
Reply with confirmation
```

---

### `bot/database.py`
**Location**: `/workspace/bot/database.py`  
**Purpose**: Async Postgres operations with connection pooling  
**Lines**: ~150

**Key methods:**
- `connect()` / `disconnect()` — Pool management
- `log_event()` — Insert event with banner/seal
- `get_user_events()` — Retrieve event history
- `search_events()` — Full-text search on banner and payload
- `get_user_stats()` — Aggregate statistics
- `store_fact()` — Persist user facts with confidence
- `get_facts()` — Retrieve active facts
- `store_memory_chunk()` — Store text with embeddings

**Pool configuration:**
- Min size: 2 connections
- Max size: 10 connections
- Command timeout: 60 seconds

---

### `bot/redis_client.py`
**Location**: `/workspace/bot/redis_client.py`  
**Purpose**: Async Redis operations for ephemeral caching  
**Lines**: ~120

**Key methods:**
- `connect()` / `disconnect()` — Connection management
- `cache_message()` — Store message with TTL (1 hour default)
- `get_recent_messages()` — Retrieve cached messages
- `set_user_context()` — Store session state (2 hour TTL)
- `get_user_context()` — Retrieve session state
- `increment_counter()` — Rate limiting support
- `get_stats()` — Cache statistics

**TTL strategy:**
- Messages: 1 hour (ephemeral)
- Context: 2 hours (session)
- Counters: 24 hours (daily)

---

### `bot/memory.py`
**Location**: `/workspace/bot/memory.py`  
**Purpose**: Orchestrates memory operations across Postgres and Redis  
**Lines**: ~100

**Key methods:**
- `get_user_stats()` — Combined DB + Redis statistics
- `search_events()` — Wrapper for event search
- `store_sealed_memory()` — Store with automatic tag extraction
- `get_context()` — Build user context from events and facts

**Tag extraction:**
- Hashtags (`#tag`)
- Ritual markers (`⟦⎊⟧`, `∎`)
- Limit: 10 tags per message

---

## 📚 Documentation

### `TELE-PROMPTR-SETUP.md`
**Location**: `/workspace/TELE-PROMPTR-SETUP.md`  
**Purpose**: Complete deployment and usage guide  
**Sections**: 15+ comprehensive sections

**Covers:**
- Quick start guide
- Architecture overview
- Database schema details
- n8n workflow setup
- Development instructions
- Security best practices
- Customization guide
- Troubleshooting
- Backup & restore
- Production deployment
- Roadmap

---

### `QUICKSTART.md`
**Location**: `/workspace/QUICKSTART.md`  
**Purpose**: 5-minute getting started guide

**Steps:**
1. Get Telegram bot token
2. Configure .env
3. Launch with docker-compose
4. Test with /start
5. View stats

---

### `.env.example`
**Location**: `/workspace/.env.example`  
**Purpose**: Environment variable template

**Variables:**
- `TELEGRAM_TOKEN` — Bot token from @BotFather (required)
- `N8N_PASSWORD` — n8n admin password (optional)
- `POSTGRES_*` — Database credentials (defaults provided)

---

## 🎯 Usage Patterns

### Ritual Message Format

```
Banner Line (first line — extracted automatically)
Content body can span multiple lines.
Tags and context go here.

Must end with seal to persist:
:: ∎
```

### Example Messages

**Daily ritual:**
```
▛//▞▞ ⟦⎊⟧ :: MORNING.RITUAL ⫸
Meditation: 20 minutes
Journaling: 3 pages
Energy level: High
:: ∎
```

**Task tracking:**
```
⟦task.update⟧ :: deploy.codex.node
Successfully deployed Telegram bot
All services healthy
Next: Import n8n workflow
:: ∎
```

**Fact storage:**
```
Personal Fact — Favorite Quote
"The Codex remembers what the mind forgets."
#wisdom #memory
:: ∎
```

---

## 🔄 Data Flow

```
1. Telegram User sends message
          ↓
2. Bot receives and parses
   - Extract banner (line 1)
   - Check for seal (:: ∎)
          ↓
3. Parallel storage:
   ┌─────────────────┬─────────────────┐
   │   Redis Cache   │  Postgres DB    │
   │   (ephemeral)   │  (permanent)    │
   │                 │                 │
   │ • Session state │ • events table  │
   │ • Recent msgs   │ • user_facts    │
   │ • Counters      │ • memory_chunks │
   └─────────────────┴─────────────────┘
          ↓
4. (Optional) n8n workflow triggered
   - Advanced orchestration
   - External integrations
          ↓
5. (Future) Embedding generation
   - OpenAI or local model
   - Store in memory_chunks.embedding
          ↓
6. Confirmation sent to user
```

---

## 🚀 Deployment Checklist

- [x] `docker-compose.yml` created
- [x] `seed.sql` schema defined
- [x] `n8n_flow.json` workflow ready
- [x] Bot application implemented
  - [x] Dockerfile
  - [x] requirements.txt
  - [x] main.py (commands + handlers)
  - [x] database.py (Postgres ops)
  - [x] redis_client.py (Redis ops)
  - [x] memory.py (orchestration)
- [x] Configuration template (.env.example)
- [x] Documentation
  - [x] Complete setup guide
  - [x] Quick start guide
  - [x] This file manifest
- [ ] Get Telegram token (user action)
- [ ] Configure .env (user action)
- [ ] Deploy: `docker-compose up -d`
- [ ] Test bot commands
- [ ] Import n8n workflow (optional)

---

## 🔐 Security Checklist

**Before production:**
- [ ] Change `POSTGRES_PASSWORD` in .env
- [ ] Set strong `N8N_PASSWORD`
- [ ] Review exposed ports in docker-compose.yml
- [ ] Consider SSL/TLS for Postgres
- [ ] Restrict network access
- [ ] Enable firewall rules
- [ ] Set up backup automation
- [ ] Review bot permissions
- [ ] Implement rate limiting
- [ ] Add monitoring/alerting

---

## 🧪 Testing Commands

```bash
# Start services
docker-compose up -d

# Check service health
docker-compose ps

# View bot logs
docker-compose logs -f bot

# Test database connection
docker exec -it codex_postgres psql -U codex -d codexdb -c "SELECT COUNT(*) FROM events;"

# Test Redis
docker exec -it codex_redis redis-cli PING

# Access n8n
open http://localhost:5678

# Stop services
docker-compose down

# Stop and remove volumes (DESTRUCTIVE)
docker-compose down -v
```

---

## 📊 Database Queries

**View recent events:**
```sql
SELECT id, ts, user_id, banner, seal
FROM events
ORDER BY ts DESC
LIMIT 20;
```

**Count sealed vs unsealed:**
```sql
SELECT 
  seal,
  COUNT(*) as count
FROM events
GROUP BY seal;
```

**User activity summary:**
```sql
SELECT 
  user_id,
  COUNT(*) as total_events,
  COUNT(CASE WHEN seal = ':: ∎' THEN 1 END) as sealed_events,
  MAX(ts) as last_activity
FROM events
GROUP BY user_id
ORDER BY last_activity DESC;
```

**Search memories:**
```sql
SELECT banner, payload->>'text' as text, ts
FROM events
WHERE user_id = '123456789'
  AND (banner ILIKE '%ritual%' OR payload::text ILIKE '%ritual%')
ORDER BY ts DESC;
```

---

## 🎨 Customization Points

### Adding Commands

**In `bot/main.py`:**
```python
self.dp.message(Command("mycommand"))(self.cmd_mycommand)

async def cmd_mycommand(self, message: Message):
    # Your logic
    await message.reply("Response :: ∎")
```

### Adding Database Tables

**In `seed.sql`:**
```sql
create table if not exists my_table(
  id bigserial primary key,
  data jsonb
);
```

### Extending Memory Manager

**In `bot/memory.py`:**
```python
async def my_custom_function(self, user_id: str):
    # Access self.db and self.redis
    return result
```

---

## 🌟 Feature Roadmap

### Phase 1: Core (✅ Complete)
- [x] Telegram bot with banner+seal parsing
- [x] Postgres + pgvector database
- [x] Redis caching
- [x] n8n workflow template
- [x] Docker Compose deployment

### Phase 2: Embeddings
- [ ] OpenAI embedding integration
- [ ] Local embedding model option (sentence-transformers)
- [ ] Automatic embedding generation on seal
- [ ] Vector similarity search

### Phase 3: Advanced Features
- [ ] Multi-user fact sharing
- [ ] Web dashboard for memory browsing
- [ ] Export to markdown/PDF
- [ ] Voice message transcription
- [ ] Image analysis and storage

### Phase 4: Intelligence
- [ ] LLM-powered auto-tagging
- [ ] Memory summarization
- [ ] Proactive recall suggestions
- [ ] Pattern detection in memories

---

## 📈 Monitoring Metrics

**Bot metrics:**
- Messages per hour
- Sealed vs unsealed ratio
- Command usage distribution
- Error rates

**Database metrics:**
- Events table size
- Memory chunks count
- Query performance
- Connection pool usage

**Redis metrics:**
- Cache hit rate
- Memory usage
- Key expiration stats

**System metrics:**
- Container CPU/memory
- Disk usage
- Network I/O

---

## 🆘 Troubleshooting Guide

### Problem: Bot not responding

**Checks:**
1. `docker-compose ps` — Is bot running?
2. `docker-compose logs bot` — Any errors?
3. Verify `TELEGRAM_TOKEN` in .env
4. Check Telegram API status

---

### Problem: Database connection failed

**Checks:**
1. `docker-compose ps postgres` — Is Postgres healthy?
2. Check `DATABASE_URL` format
3. Verify credentials match docker-compose.yml
4. Test: `docker exec -it codex_postgres pg_isready`

---

### Problem: Messages not persisting

**Checks:**
1. Is message sealed with `:: ∎`?
2. Check bot logs for errors
3. Query events: `SELECT COUNT(*) FROM events;`
4. Verify database connection

---

### Problem: n8n workflow not triggering

**Checks:**
1. Is workflow activated in n8n UI?
2. Are credentials configured?
3. Check n8n logs: `docker-compose logs n8n`
4. Test Postgres connection in n8n

---

## 📚 Additional Resources

**Technologies used:**
- [aiogram](https://docs.aiogram.dev/) — Async Telegram Bot framework
- [asyncpg](https://magicstack.github.io/asyncpg/) — Async PostgreSQL driver
- [pgvector](https://github.com/pgvector/pgvector) — Vector similarity search
- [n8n](https://docs.n8n.io/) — Workflow automation
- [Redis](https://redis.io/docs/) — In-memory data store

**Related concepts:**
- Vector embeddings and semantic search
- Ritual computing and prompt design
- Personal knowledge management (PKM)
- Memory augmentation systems

---

## ✅ Verification

**All files created and ready:**

```
/workspace/
├── docker-compose.yml ✅
├── seed.sql ✅
├── n8n_flow.json ✅
├── .env.example ✅
├── TELE-PROMPTR-SETUP.md ✅
├── QUICKSTART.md ✅
├── TELE-PROMPTR-FILES.md ✅ (this file)
└── bot/
    ├── Dockerfile ✅
    ├── requirements.txt ✅
    ├── main.py ✅
    ├── database.py ✅
    ├── redis_client.py ✅
    └── memory.py ✅
```

**Total files**: 13  
**Total lines of code**: ~1,500+  
**Total documentation**: ~3,000+ words

---

**▛//▞▞ All Files Sealed. Research Complete. Ready to Deploy. ⫸**

:: ∎
