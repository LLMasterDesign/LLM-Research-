# ▛//▞▞ ⟦⎊⟧ :: TELE-PROMPTR UPGRADE FILES ⫸

**Telegram Codex Memory Node** — Complete deployment guide for banner+seal ritual memory persistence with Redis, Postgres (pgvector), and n8n orchestration.

---

## 📋 Overview

This system creates a Telegram bot that:
- **Accepts ritual-formatted messages** with banners and seals (`:: ∎`)
- **Persists sealed memories** to Postgres with pgvector for embeddings
- **Caches ephemeral data** in Redis
- **Orchestrates workflows** via n8n
- **Maintains audit trails** with drift-lock guarantees

---

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose installed
- Telegram account
- Basic terminal/command line knowledge

### 2. Get Your Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow prompts
3. Choose a name and username for your bot
4. Copy the token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Telegram token
nano .env  # or use your favorite editor
```

Add your token:
```
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
N8N_PASSWORD=your_secure_password
```

### 4. Launch the Stack

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bot
```

### 5. Verify Services

- **Bot**: Should connect to Telegram
- **Postgres**: Running on port 5432
- **Redis**: Running on port 6379
- **n8n**: Web UI at http://localhost:5678

---

## 🎯 Usage

### Message Format

Every message follows the **banner + seal** ritual:

```
▛//▞▞ ⟦⎊⟧ :: YOUR.BANNER.HERE ⫸
Your message content goes here.
Multiple lines are supported.

Only messages ending with the seal are persisted:
:: ∎
```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize your Codex |
| `/help` | Show help message |
| `/stats` | View your memory statistics |
| `/recall [query]` | Search your sealed memories |

### Examples

**Sealed Memory** (will be persisted):
```
Morning Ritual — 2025-10-04
Completed meditation and journaling.
Ready to deploy Codex node.
:: ∎
```

**Unsealed Message** (ephemeral, won't persist):
```
Just testing the bot
```

---

## 🏗️ Architecture

### Services

1. **PostgreSQL + pgvector** (`codex_postgres`)
   - Stores events, facts, and memory chunks
   - Supports vector embeddings for semantic search
   - Schema auto-initializes from `seed.sql`

2. **Redis** (`codex_redis`)
   - Ephemeral session cache
   - Message history buffer
   - User context storage

3. **Bot Worker** (`codex_bot`)
   - Python aiogram-based Telegram bot
   - Handles banner extraction and seal validation
   - Orchestrates memory persistence

4. **n8n** (`codex_n8n`)
   - Workflow automation
   - Advanced orchestration (optional)
   - Web UI for visual workflows

### Data Flow

```
Telegram Message
    ↓
Bot extracts banner & validates seal
    ↓
┌─────────────┬─────────────┐
│   Redis     │  Postgres   │
│ (ephemeral) │ (permanent) │
└─────────────┴─────────────┘
    ↓
n8n workflows (optional)
    ↓
Embedding generation (future)
    ↓
Vector storage in memory_chunks
```

---

## 📊 Database Schema

### Tables

**`events`** — All user interactions
```sql
id, ts, user_id, kind, banner, seal, payload
```

**`user_facts`** — Persisted facts with confidence scores
```sql
user_id, key, value, confidence, sealed_at, revoked_at
```

**`memory_chunks`** — Text + embeddings for semantic search
```sql
id, user_id, banner, tags, text, embedding (vector)
```

---

## 🔧 n8n Workflow Setup

1. Open n8n at http://localhost:5678
2. Login with credentials from `.env`
3. Click **Import from File**
4. Select `n8n_flow.json`
5. Configure credentials:
   - **Telegram Bot API**: Your bot token
   - **Postgres Codex**: Connection to postgres service

The workflow will:
- Listen for Telegram messages
- Extract banner and seal
- Log to `events` table
- Reply with confirmation

---

## 🛠️ Development

### Project Structure

```
.
├── docker-compose.yml      # Service definitions
├── seed.sql                # Database initialization
├── n8n_flow.json          # n8n workflow template
├── .env.example           # Environment template
├── bot/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py           # Bot entry point
│   ├── database.py       # Postgres operations
│   ├── redis_client.py   # Redis operations
│   └── memory.py         # Memory orchestration
└── TELE-PROMPTR-SETUP.md # This file
```

### Local Development

```bash
# Install dependencies locally (optional)
cd bot
pip install -r requirements.txt

# Run bot directly (requires services running)
export TELEGRAM_TOKEN="your_token"
export DATABASE_URL="postgres://codex:changeme@localhost:5432/codexdb"
export REDIS_URL="redis://localhost:6379/0"
python main.py
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f bot
docker-compose logs -f postgres
docker-compose logs -f n8n
```

### Database Access

```bash
# Connect to Postgres
docker exec -it codex_postgres psql -U codex -d codexdb

# View events
SELECT * FROM events ORDER BY ts DESC LIMIT 10;

# View user facts
SELECT * FROM user_facts WHERE revoked_at IS NULL;
```

### Redis CLI

```bash
# Connect to Redis
docker exec -it codex_redis redis-cli

# List keys
KEYS *

# Get message
GET msg:123456789:1234567890.123
```

---

## 🔐 Security Best Practices

1. **Change default passwords** in `.env`:
   - `POSTGRES_PASSWORD`
   - `N8N_PASSWORD`

2. **Restrict port exposure** in production:
   - Remove or bind Postgres/Redis to localhost only
   - Use reverse proxy for n8n

3. **Enable SSL/TLS** for production deployments

4. **Regular backups** of Postgres data:
   ```bash
   docker exec codex_postgres pg_dump -U codex codexdb > backup.sql
   ```

5. **Token security**:
   - Never commit `.env` file
   - Use environment variables or secrets management

---

## 🎨 Customization

### Adding Custom Commands

Edit `bot/main.py`:

```python
self.dp.message(Command("custom"))(self.cmd_custom)

async def cmd_custom(self, message: Message):
    # Your logic here
    await message.reply("Custom response :: ∎")
```

### Extending Database Schema

1. Add migration SQL to `seed.sql`
2. Rebuild: `docker-compose down && docker-compose up -d`

### Adding Embeddings

Install OpenAI or local embedding model:

```python
# In bot/memory.py
import openai

async def generate_embedding(self, text: str):
    response = await openai.Embedding.acreate(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']
```

---

## 🐛 Troubleshooting

### Bot Won't Start

```bash
# Check token
docker-compose logs bot | grep TOKEN

# Verify services are healthy
docker-compose ps
```

### Database Connection Failed

```bash
# Check Postgres is running
docker-compose ps postgres

# Test connection
docker exec -it codex_postgres psql -U codex -d codexdb -c "SELECT 1;"
```

### n8n Can't Connect to Postgres

- Ensure host is `postgres` (not `localhost`)
- Verify credentials match `docker-compose.yml`
- Check network connectivity: `docker network ls`

### Messages Not Persisting

- Verify seal format: `:: ∎` (with space)
- Check bot logs for errors
- Query events table directly

---

## 📚 Ritual Structure Reference

### Banner Format

First line of every message. Examples:

```
▛//▞▞ ⟦⎊⟧ :: DAILY.RITUAL ⫸
Morning Standup — 2025-10-04
⟦task.update⟧ :: project.deploy
```

### Seal Format

End messages with:
```
:: ∎
```

Without seal, messages are:
- Received by bot
- Cached in Redis
- NOT persisted to Postgres
- NOT searchable later

---

## 🚢 Production Deployment

### Docker Compose (Production)

1. Use external volumes for persistence
2. Enable automatic restart policies
3. Add health checks
4. Use secrets instead of environment variables

### Kubernetes

Deploy with StatefulSets for databases:
- Postgres: StatefulSet with PVC
- Redis: StatefulSet with PVC
- Bot: Deployment
- n8n: Deployment with Ingress

### Monitoring

Add observability stack:
- Prometheus for metrics
- Grafana for dashboards
- Loki for log aggregation

---

## 🔄 Backup & Restore

### Backup

```bash
# Postgres dump
docker exec codex_postgres pg_dump -U codex -d codexdb -F c -f /tmp/backup.dump
docker cp codex_postgres:/tmp/backup.dump ./backup-$(date +%Y%m%d).dump

# Redis snapshot
docker exec codex_redis redis-cli BGSAVE
docker cp codex_redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

### Restore

```bash
# Postgres restore
docker cp backup.dump codex_postgres:/tmp/
docker exec codex_postgres pg_restore -U codex -d codexdb -c /tmp/backup.dump

# Redis restore
docker cp redis-backup.rdb codex_redis:/data/dump.rdb
docker-compose restart redis
```

---

## 📈 Roadmap

- [ ] Embedding generation (OpenAI/local)
- [ ] Vector similarity search
- [ ] Multi-user fact sharing
- [ ] Web dashboard for memories
- [ ] Voice message support
- [ ] Automated tagging with LLM
- [ ] Export to markdown/PDF

---

## 🤝 Contributing

This is a drift-locked ritual structure. Modifications should:
1. Preserve banner + seal format
2. Maintain backward compatibility
3. Update `seed.sql` schema version
4. Add migration paths

---

## 📜 License

This Codex implementation is provided as-is for personal and educational use.

---

## 🆘 Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify `.env` configuration
3. Test database connection
4. Review this documentation

---

**▛//▞▞ The Codex is Sealed. Your Memory Persists. ⫸**

:: ∎
