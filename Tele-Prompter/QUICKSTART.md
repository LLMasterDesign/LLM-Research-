# ⚡ QUICKSTART: Deploy in 60 Seconds

**One-shot deployment of Glyph-It Forge on any server with Docker!**

---

## 🎯 What You Get

- 🤖 Telegram bot (Python)
- 🗄️ PostgreSQL database (15 pre-loaded glyphs)
- 🔄 n8n automation (webhooks, daily reports)
- ⚡ Redis cache
- 📊 Analytics views
- 🏆 Achievement system

**All in ONE command!**

---

## 🚀 Deploy Now

### Step 1: Get Files (10 seconds)
```bash
# If you have git
git clone <your-repo-url>
cd Tele-Prompter

# Or download and extract ZIP
cd Tele-Prompter
```

### Step 2: Configure (20 seconds)
```bash
# Copy environment template
cp .env.example .env

# Edit with your bot token
nano .env
# or on Windows:
notepad .env

# REQUIRED: Set this line
TELEGRAM_BOT_TOKEN=paste_your_token_here
```

**Get your bot token:**
1. Message `@BotFather` on Telegram
2. Send `/newbot`
3. Follow prompts
4. Copy the token BotFather gives you

### Step 3: Launch (30 seconds)
```bash
# Start everything!
docker-compose up -d

# Watch it come alive
docker-compose logs -f
```

---

## ✅ Verify It's Working

### Check All Services Running:
```bash
docker-compose ps
```

Expected output:
```
NAME                STATUS
glyph_forge_bot     running
glyph_db            running (healthy)
glyph_n8n           running
glyph_redis         running
```

### Test Your Bot:
1. Open Telegram
2. Find your bot (`@your_bot_name`)
3. Send `/start`
4. See menu with buttons? **SUCCESS!** 🎉

### Test Database (15 seeded glyphs):
```bash
docker-compose exec db psql -U glyph -d glyphforge -c \
  "SELECT name, token_count FROM glyphs WHERE is_featured = TRUE;"
```

### Access n8n Dashboard:
- Open: `http://YOUR_SERVER_IP:5678`
- Login: admin / glyphadmin
- Import workflow: `glyph-forge-workflow.json`

---

## 🎮 What Can You Do Now?

### In Telegram:
- `/start` - Open main menu
- `/forge` - Create a glyph
- `/list` - View your glyphs
- `/stats` - See statistics
- `/help` - Get help

### In n8n (localhost:5678):
- Daily reports at 9am
- Webhook for glyph events
- Streak checking every 5 minutes
- AI compression endpoint

### In Database:
- Browse 15 pre-loaded glyphs
- Track all usage
- View analytics
- Check achievements

---

## 📁 File Structure

```
Tele-Prompter/
├── docker-compose.yml      # ⚙️ Main config
├── seed.sql                # 📊 Database setup
├── glyph-forge-workflow.json # 🔄 n8n automation
├── .env.example            # 🔧 Config template
├── bot/
│   └── __main__.py         # 🤖 Bot code
├── DEPLOY.md               # 📖 Full deployment guide
├── QUICKSTART.md           # ⚡ This file
└── FEATURE_RESEARCH.md     # 💡 90+ feature ideas
```

---

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f glyph-bot

# Restart bot
docker-compose restart glyph-bot

# Stop everything
docker-compose down

# Start again
docker-compose up -d

# Database backup
docker-compose exec db pg_dump -U glyph glyphforge > backup.sql

# Check what's running
docker-compose ps

# See resource usage
docker stats
```

---

## 🔧 Quick Fixes

### Bot not responding?
```bash
# Check logs
docker-compose logs glyph-bot

# Restart
docker-compose restart glyph-bot

# Make sure token is correct in .env
cat .env | grep TELEGRAM_BOT_TOKEN
```

### Can't access n8n?
```bash
# Check if running
docker-compose ps n8n

# Check port is open (Windows)
netstat -an | findstr :5678

# Restart n8n
docker-compose restart n8n
```

### Database issues?
```bash
# Check database health
docker-compose exec db pg_isready -U glyph

# Connect to database
docker-compose exec db psql -U glyph -d glyphforge

# View tables
\dt

# Exit
\q
```

---

## 🎯 Next Steps

1. ✅ Bot is working → Test all commands
2. ✅ Database has data → Query some glyphs
3. ✅ n8n is accessible → Import workflow
4. 📖 Read [DEPLOY.md](./DEPLOY.md) for detailed docs
5. 💡 Check [FEATURE_RESEARCH.md](./FEATURE_RESEARCH.md) for more features
6. 🚀 Invite friends to test your bot!

---

## 💡 Pro Tips

### Change n8n Password
```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Find and change:
N8N_BASIC_AUTH_PASSWORD=glyphadmin  # Change this!

# Restart
docker-compose restart n8n
```

### Enable AI Compression
```bash
# Add OpenAI key to .env
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Restart bot
docker-compose restart glyph-bot
```

### Set Up Daily Reports
```bash
# Edit .env with your Telegram chat ID
echo "ADMIN_CHAT_ID=your_chat_id" >> .env

# Get your chat ID from @userinfobot

# Restart n8n
docker-compose restart n8n
```

---

## 🆘 Need Help?

### Full Documentation
- [DEPLOY.md](./DEPLOY.md) - Complete deployment guide
- [FEATURE_RESEARCH.md](./FEATURE_RESEARCH.md) - 90+ features
- [IMPLEMENTATION_EXAMPLES.md](./IMPLEMENTATION_EXAMPLES.md) - Code samples

### Check Logs
```bash
# All services
docker-compose logs

# Specific service with follow
docker-compose logs -f glyph-bot
docker-compose logs -f db
docker-compose logs -f n8n
```

### Test Components
```bash
# Test database
docker-compose exec db psql -U glyph -d glyphforge -c "SELECT COUNT(*) FROM glyphs;"

# Test Redis
docker-compose exec redis redis-cli ping
# Should return: PONG

# Test n8n webhook
curl -X POST http://localhost:5678/webhook/glyph-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","user_id":123}'
```

---

## 🎉 Success Checklist

- [ ] All containers running (`docker-compose ps`)
- [ ] Bot responds to `/start` in Telegram
- [ ] Database has 15 featured glyphs
- [ ] n8n dashboard accessible
- [ ] Can create a glyph with `/forge`
- [ ] Glyph shows up in `/list`
- [ ] Stats display with `/stats`

**All checked?** You're ready to forge glyphs! 🔨✨

---

## 📊 What's Seeded in Database?

15 pre-made glyphs across categories:
- `code_wizard` - Programming expert (13 tokens)
- `creative_muse` - Artistic inspiration (11 tokens)
- `debug_master` - Bug finder (11 tokens)
- `story_weaver` - Narrative crafter (10 tokens)
- `data_sage` - Data analyst (10 tokens)
- `perfect_27` - **Exactly 27 tokens!** 🎯
- And 9 more...

All ready to test immediately!

---

## 🚀 You're Live!

Your Glyph-It Forge is running at:
- **Bot:** Talk to it on Telegram
- **n8n:** `http://YOUR_IP:5678`
- **Database:** `localhost:5432`
- **Redis:** `localhost:6379`

**Now go create some glyphs!** ⚡

---

*Deployed in 60 seconds. Forging for a lifetime.* 🔨✨
