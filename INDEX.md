# ▛//▞▞ ⟦⎊⟧ :: TELE-PROMPTR INDEX ⫸

**Quick navigation for Telegram Codex Memory Node project**

---

## 🚀 Start Here

### For New Users
1. **[QUICKSTART.md](QUICKSTART.md)** — Get running in 5 minutes
2. **[DEPLOYMENT-STEPS.md](DEPLOYMENT-STEPS.md)** — Detailed step-by-step guide

### For Deep Dive
- **[TELE-PROMPTR-SETUP.md](TELE-PROMPTR-SETUP.md)** — Complete documentation (architecture, customization, troubleshooting)
- **[TELE-PROMPTR-FILES.md](TELE-PROMPTR-FILES.md)** — File manifest and technical reference

---

## 📁 File Structure

```
/workspace/
│
├── 📘 Documentation
│   ├── INDEX.md                    ← You are here
│   ├── QUICKSTART.md               ← 5-minute start
│   ├── DEPLOYMENT-STEPS.md         ← Step-by-step
│   ├── TELE-PROMPTR-SETUP.md       ← Complete guide
│   └── TELE-PROMPTR-FILES.md       ← File manifest
│
├── ⚙️ Infrastructure
│   ├── docker-compose.yml          ← Service definitions
│   ├── seed.sql                    ← Database schema
│   ├── n8n_flow.json              ← Workflow template
│   └── .env.example               ← Config template
│
└── 🤖 Bot Application (./bot/)
    ├── Dockerfile                  ← Container build
    ├── requirements.txt            ← Dependencies
    ├── main.py                     ← Entry point
    ├── database.py                 ← Postgres ops
    ├── redis_client.py            ← Redis cache
    └── memory.py                  ← Orchestration
```

---

## 🎯 Quick Commands

### Deploy
```bash
cp .env.example .env        # Configure
nano .env                   # Add Telegram token
docker-compose up -d        # Launch
docker-compose logs -f bot  # Watch logs
```

### Test
```bash
# Send to your Telegram bot:
/start
/help
/stats
```

### Manage
```bash
docker-compose ps           # Check status
docker-compose logs bot     # View logs
docker-compose restart bot  # Restart bot
docker-compose down         # Stop all
```

---

## 📊 What You Get

### Services
- ✅ **Postgres + pgvector** — Vector-enabled database
- ✅ **Redis** — Ephemeral cache
- ✅ **Telegram Bot** — Message handler with ritual parsing
- ✅ **n8n** — Workflow automation (optional)

### Features
- ✅ Banner extraction (first line)
- ✅ Seal validation (`:: ∎`)
- ✅ Event logging
- ✅ Memory persistence
- ✅ Search & recall
- ✅ User statistics

### Bot Commands
| Command | Purpose |
|---------|---------|
| `/start` | Initialize Codex |
| `/help` | Show help |
| `/stats` | View statistics |
| `/recall [query]` | Search memories |

---

## 💡 Message Format

**Sealed (persists to database):**
```
Banner Line — First line is auto-extracted
Your content goes here.
Multiple lines supported.
:: ∎
```

**Unsealed (ephemeral only):**
```
Regular message without seal.
Will be cached in Redis but not persisted.
```

---

## 🔑 Key Concepts

### Banner
- First line of every message
- Automatically extracted
- Used for categorization and search
- Examples: `Morning Ritual`, `Task Update`, `Daily Log`

### Seal
- Marker: `:: ∎`
- Indicates message should persist
- Only sealed messages stored permanently
- Unsealed messages are cached temporarily

### Events
- Every interaction logged
- Includes banner, seal, timestamp
- Queryable and searchable
- Forms memory history

### Facts
- Key-value pairs
- Confidence scoring
- Revocable (soft delete)
- Timestamped seals

### Memory Chunks
- Text storage with metadata
- Tag-based categorization
- Vector embeddings (future)
- Semantic search ready

---

## 🏗️ Architecture

```
User (Telegram)
      ↓
   Bot Worker
   /        \
Redis      Postgres
(temp)    (permanent)
   \        /
    n8n Workflows
        ↓
   (Future: Embeddings)
```

---

## 🛠️ Customization

### Add Bot Command
Edit `bot/main.py`:
```python
self.dp.message(Command("custom"))(self.cmd_custom)

async def cmd_custom(self, message: Message):
    await message.reply("Custom response :: ∎")
```

### Add Database Table
Edit `seed.sql`:
```sql
create table if not exists my_table(
  id bigserial primary key,
  data jsonb
);
```

### Extend Memory Manager
Edit `bot/memory.py`:
```python
async def my_function(self, user_id: str):
    # Your logic
    return result
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not responding | Check `TELEGRAM_TOKEN` in `.env` |
| Database error | Verify services: `docker-compose ps` |
| Messages not saving | Ensure seal: `:: ∎` |
| n8n workflow fails | Configure credentials in n8n UI |

**Full troubleshooting:** See [TELE-PROMPTR-SETUP.md](TELE-PROMPTR-SETUP.md)

---

## 📚 Documentation Map

### Quick References
- **[INDEX.md](INDEX.md)** ← You are here
- **[QUICKSTART.md](QUICKSTART.md)** — Fastest path to running
- **[DEPLOYMENT-STEPS.md](DEPLOYMENT-STEPS.md)** — Detailed deployment

### Comprehensive Guides
- **[TELE-PROMPTR-SETUP.md](TELE-PROMPTR-SETUP.md)**
  - Architecture deep dive
  - Database schema reference
  - Security best practices
  - Customization guide
  - Production deployment
  - Backup & restore
  - Roadmap

- **[TELE-PROMPTR-FILES.md](TELE-PROMPTR-FILES.md)**
  - File-by-file breakdown
  - Code explanations
  - Data flow diagrams
  - Database queries
  - Monitoring metrics
  - Feature roadmap

---

## 🔐 Security Checklist

Before production:
- [ ] Change `POSTGRES_PASSWORD` in `.env`
- [ ] Set strong `N8N_PASSWORD`
- [ ] Restrict port exposure
- [ ] Enable SSL/TLS
- [ ] Configure firewall
- [ ] Set up backups
- [ ] Add monitoring

---

## 🚀 Next Steps

### Immediate
1. Get Telegram token
2. Deploy with Docker Compose
3. Test basic commands
4. Send first sealed message

### Short Term
1. Import n8n workflow
2. Customize bot commands
3. Set up regular backups
4. Add monitoring

### Long Term
1. Add embedding generation
2. Implement semantic search
3. Build web dashboard
4. Deploy to production
5. Scale horizontally

---

## 📊 Project Stats

- **Files Created**: 14
- **Code Lines**: ~1,500+
- **Documentation**: ~15,000+ words
- **Services**: 4
- **Database Tables**: 3
- **Bot Commands**: 4
- **Development Time**: Ready to deploy ✅

---

## 🆘 Need Help?

1. **Read documentation** — Start with QUICKSTART.md
2. **Check logs** — `docker-compose logs -f`
3. **Verify config** — Check `.env` file
4. **Test services** — `docker-compose ps`
5. **Review guides** — See TELE-PROMPTR-SETUP.md

---

## 📜 License & Usage

This implementation is provided as-is for personal and educational use. The ritual structure (banner + seal) should be preserved when extending.

---

**▛//▞▞ ⟦⎊⟧ :: Navigate with purpose. Build with intention. Seal with confidence. ⫸**

:: ∎
