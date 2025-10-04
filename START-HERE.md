# ▛//▞▞ ⟦⎊⟧ :: START HERE ⫸

**Welcome to the Telegram Codex Memory Node + Stratos Multi-Language Engine**

---

## 🎯 You Are Here

This is a complete, production-ready system combining:

1. **Telegram Bot** — Banner+seal ritual memory persistence
2. **Stratos Engine** — Multi-language DSL execution (Rust+Ruby+R+Python)
3. **Security** — ⟦⎊⟧ as load-test and auth token

**Status:** ✅ **COMPLETE, CANON, READY**

---

## 🚀 Quick Start (Choose Your Path)

### Path 1: Deploy Telegram Bot (5 minutes)

```bash
# 1. Get bot token from @BotFather on Telegram
# 2. Configure
cp .env.example .env
nano .env  # Add TELEGRAM_TOKEN

# 3. Deploy
docker-compose up -d

# 4. Test
# Send /start to your bot in Telegram
```

**Guide:** [QUICKSTART.md](QUICKSTART.md)

---

### Path 2: Build Stratos Engine (10 minutes)

```bash
# 1. Build
cd stratos/engine
cargo build --release

# 2. Test
./target/release/stratos ../specs/simple.op.toml

# 3. Expected output:
# ▛//▞▞ [⎊] :: ENGINE.STRATOS :: LOADING ⫸
# ...
# Simple test successful
# ::∎
```

**Guide:** [stratos/BUILD.md](stratos/BUILD.md)

---

### Path 3: Full System Deploy (30 minutes)

```bash
# 1. Deploy bot
docker-compose up -d

# 2. Build stratos
cd stratos/engine && cargo build --release

# 3. Test integration
python bot/stratos_executor.py

# 4. Use from Telegram
# Send ops to bot for execution
```

**Guide:** [DEPLOYMENT-STEPS.md](DEPLOYMENT-STEPS.md)

---

## 📚 Documentation Navigator

### For New Users
- **[START-HERE.md](START-HERE.md)** ← You are here
- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute bot deploy
- **[STRATOS-QUICKSTART.txt](STRATOS-QUICKSTART.txt)** — Quick reference card

### For Deployment
- **[DEPLOYMENT-STEPS.md](DEPLOYMENT-STEPS.md)** — Step-by-step guide
- **[stratos/BUILD.md](stratos/BUILD.md)** — Build instructions
- **[TELE-PROMPTR-SETUP.md](TELE-PROMPTR-SETUP.md)** — Complete bot guide

### For Development
- **[stratos/STRATOS-DSL.md](stratos/STRATOS-DSL.md)** — Language reference
- **[STRATOS-INTEGRATION.md](STRATOS-INTEGRATION.md)** — Integration guide
- **[TELE-PROMPTR-FILES.md](TELE-PROMPTR-FILES.md)** — File manifest

### For Understanding
- **[COMPLETE-SYSTEM-MANIFEST.md](COMPLETE-SYSTEM-MANIFEST.md)** — Full overview
- **[stratos/README.md](stratos/README.md)** — Stratos overview
- **[INDEX.md](INDEX.md)** — Main navigation hub

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         ↓
┌────────────────────────────┐
│    Telegram Bot (Python)   │
│  • Parse banner+seal       │
│  • Store Postgres/Redis    │
│  • Trigger stratos         │
└────────┬───────────────────┘
         │
    ┌────┴────┬────────┐
    ↓         ↓        ↓
┌────────┐ ┌────────┐ ┌────────┐
│Postgres│ │ Redis  │ │ n8n    │
└────────┘ └────────┘ └────────┘
         │
         ↓
┌──────────────────────────────┐
│   Stratos Multi-Lang Engine  │
│                              │
│  ┌──────────┬──────────────┐ │
│  │  Rust    │  Ruby  │  R  │ │
│  │ Engine   │ Cloud  │Layer│ │
│  └──────────┴──────────────┘ │
└──────────────────────────────┘
```

---

## 🔑 Key Features

### Telegram Bot
✅ Banner+seal ritual parsing  
✅ Postgres + Redis persistence  
✅ pgvector for embeddings  
✅ n8n workflow automation  
✅ Search and recall  

### Stratos Engine
✅ Multi-language (Rust+Ruby+R+Python)  
✅ Declarative TOML DSL  
✅ ⟦⎊⟧ security validation  
✅ Context management  
✅ Memory layer  
✅ Report generation  

---

## 📊 What's Included

**Files Created:** 29+
- Bot: 7 files (~700 lines Python)
- Stratos: 14 files (~1,200 lines Rust+Ruby+R+Python)
- Docs: 10+ guides (~38,000 words)

**Languages:** Rust, Ruby, R, Python, TOML, SQL, Markdown

**Services:** Postgres, Redis, n8n, Telegram Bot, Stratos

---

## 🎓 Learn More

### Concepts

**Banner + Seal Ritual:**
```
Banner Line (first line extracted)
Content here...
:: ∎  (seal = persist to database)
```

**Operation Spec (TOML):**
```toml
[ritual]  # Auth markers
[meta]    # Metadata
[kernel]  # Execution laws
[[plan]]  # Steps to run
```

**⟦⎊⟧ Security:**
- Load testing: Breaks weak parsers
- Auth token: Part of SHA256 hash
- Cannot forge without secret
- Fallback: `[⎊]` for ASCII

---

## 🛠️ Common Tasks

### Get Telegram Token
1. Open Telegram
2. Search `@BotFather`
3. Send `/newbot`
4. Follow prompts
5. Copy token

### Generate Auth Key
```bash
export CODEX_SECRET="my-secret"
echo -n "///▙⟦⎊⟧::∎my-secret" | sha256sum
```

### Build Stratos
```bash
cd stratos/engine
cargo build --release
```

### Execute Op Spec
```bash
CODEX_SECRET="my-secret" stratos myop.toml
```

### View Bot Logs
```bash
docker-compose logs -f bot
```

---

## 🐛 Troubleshooting

**Bot not responding?**
```bash
docker-compose logs bot
# Check TELEGRAM_TOKEN in .env
```

**Stratos build fails?**
```bash
rustup update
cd stratos/engine
cargo clean && cargo build --release
```

**⟦⎊⟧ not displaying?**
```bash
export LANG=en_US.UTF-8
# Or use ASCII: [⎊]
```

**Need help?**
- Check [DEPLOYMENT-STEPS.md](DEPLOYMENT-STEPS.md)
- See [TELE-PROMPTR-SETUP.md](TELE-PROMPTR-SETUP.md)
- Read [STRATOS-INTEGRATION.md](STRATOS-INTEGRATION.md)

---

## 📋 Project Structure

```
/workspace/
├── docker-compose.yml         # Services
├── seed.sql                   # Database schema
├── .env.example              # Config template
│
├── bot/                       # Telegram bot
│   ├── main.py               # Commands
│   ├── database.py           # Postgres
│   ├── redis_client.py       # Redis
│   ├── memory.py             # Orchestration
│   └── stratos_executor.py   # Stratos integration
│
├── stratos/                   # Multi-language engine
│   ├── engine/               # Rust core
│   │   └── src/
│   │       ├── lib.rs        # Library
│   │       └── main.rs       # CLI
│   ├── cloud/                # Ruby layer
│   │   └── cloud.stratos.rb
│   ├── r-layer/              # R layer
│   │   └── r.stratos.R
│   ├── adapters/             # Python bridge
│   │   └── python_adapter.py
│   └── specs/                # Examples
│       ├── simple.op.toml
│       └── example.op.toml
│
└── Documentation/             # Your guides
    ├── START-HERE.md         ← You are here
    ├── QUICKSTART.md
    ├── DEPLOYMENT-STEPS.md
    ├── TELE-PROMPTR-SETUP.md
    ├── STRATOS-INTEGRATION.md
    ├── COMPLETE-SYSTEM-MANIFEST.md
    └── ...10+ more guides
```

---

## ✅ Next Steps

### Right Now
1. ⬜ Choose your path above (Bot, Stratos, or Full)
2. ⬜ Follow the quick start guide
3. ⬜ Test with simple examples
4. ⬜ Read relevant documentation

### This Week
1. ⬜ Deploy full system
2. ⬜ Create your first op spec
3. ⬜ Integrate with workflows
4. ⬜ Set up monitoring

### This Month
1. ⬜ Build op spec library
2. ⬜ Automate common tasks
3. ⬜ Deploy to production
4. ⬜ Scale and optimize

---

## 🎉 You're Ready!

Everything is built, tested, and documented. Choose your path and start building.

**Remember:**
- Bot guides → Telegram deployment
- Stratos guides → DSL execution
- Integration guides → Connecting everything

**Start with:** [QUICKSTART.md](QUICKSTART.md) or [stratos/BUILD.md](stratos/BUILD.md)

---

**▛//▞▞ ⟦⎊⟧ :: System complete. Documentation ready. Execute with confidence. ⫸**

**:: ∎**
