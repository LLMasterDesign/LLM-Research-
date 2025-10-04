# 🚀 One-Shot Deployment Guide

Deploy Glyph-It Forge on your RDP/VPS in under 5 minutes!

---

## ⚡ Quick Start

### 1. Prerequisites Check
```bash
# Check Docker is installed
docker --version
docker-compose --version

# If not installed, install Docker:
# Windows: Download Docker Desktop
# Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
```

### 2. Setup (2 minutes)
```bash
# Clone/download files to your RDP
cd /path/to/Tele-Prompter

# Copy and edit environment file
cp .env.example .env
nano .env  # or use notepad on Windows

# REQUIRED: Set your Telegram bot token
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz

# Optional: Set OpenAI key for AI compression
OPENAI_API_KEY=sk-...
```

### 3. Launch Everything (1 command!)
```bash
docker-compose up -d
```

That's it! 🎉

---

## 📊 What Just Happened?

Your deployment includes:

### 🤖 **Telegram Bot** (Port: Internal)
- Python-based bot ready to receive commands
- Connected to PostgreSQL database
- Webhook integration with n8n

### 🗄️ **PostgreSQL Database** (Port: 5432)
- Pre-seeded with 15 featured glyphs
- Achievement system ready
- Analytics views configured
- Test user included

### 🔄 **n8n Automation** (Port: 5678)
- Webhook for glyph events
- Daily report scheduler (9am)
- Streak checker (every 5 minutes)
- AI compression endpoint
- Achievement notifications

### ⚡ **Redis Cache** (Port: 6379)
- Fast data caching
- Session management
- Queue system ready

---

## 🔍 Verify Deployment

### Check all services are running:
```bash
docker-compose ps
```

You should see:
```
     Name                   State           Ports
----------------------------------------------------------------
glyph_forge_bot     Up
glyph_db            Up (healthy)   0.0.0.0:5432->5432/tcp
glyph_n8n           Up             0.0.0.0:5678->5678/tcp
glyph_redis         Up             0.0.0.0:6379->6379/tcp
```

### Check logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f glyph-bot
docker-compose logs -f db
docker-compose logs -f n8n
```

### Test database connection:
```bash
docker-compose exec db psql -U glyph -d glyphforge -c "SELECT COUNT(*) FROM glyphs WHERE is_featured = TRUE;"
```

Should return: `15` featured glyphs

---

## 🎮 Access Points

### **Telegram Bot**
1. Open Telegram
2. Search for your bot: `@your_bot_name`
3. Send `/start`
4. Should see welcome menu! 🎉

### **n8n Dashboard**
1. Open browser: `http://YOUR_SERVER_IP:5678`
2. Login:
   - Username: `admin`
   - Password: `glyphadmin` (change this!)
3. Import workflow:
   - Click "+" → "Import from File"
   - Select `glyph-forge-workflow.json`
   - Click "Save"
4. Activate workflow (toggle switch)

### **Database (if needed)**
```bash
# Connect to database
docker-compose exec db psql -U glyph -d glyphforge

# Run queries
glyphforge=# SELECT * FROM v_popular_glyphs LIMIT 5;
glyphforge=# \q  # to exit
```

---

## 🔧 Configuration

### Change n8n Password
```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Find these lines:
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=glyphadmin  # Change this!

# Restart
docker-compose restart n8n
```

### Add OpenAI for AI Compression
```bash
# Edit .env
nano .env

# Add your key
OPENAI_API_KEY=sk-your-real-key-here

# Restart bot
docker-compose restart glyph-bot
```

### Set Admin Chat for Reports
```bash
# Get your Telegram chat ID
# 1. Message @userinfobot on Telegram
# 2. Copy your ID

# Edit .env
ADMIN_CHAT_ID=-1001234567890  # Replace with your ID

# Restart
docker-compose restart n8n
```

---

## 📝 Create Minimal Bot Code

Since we're using a slim image, create the bot code:

```bash
# Create bot directory
mkdir -p bot

# Create main bot file
nano bot/__main__.py
```

Paste this minimal bot code:

```python
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Glyph-It Forge Bot\n\n"
        "Connected and ready!\n"
        "Use /help for commands."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Commands:\n"
        "/start - Start bot\n"
        "/help - Show this help\n"
        "/status - Bot status"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running!")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('status', status))
    
    logger.info("🚀 Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
```

Save and restart:
```bash
docker-compose restart glyph-bot
```

---

## 🧪 Test Everything

### 1. Test Bot
```bash
# Send /start to your bot on Telegram
# Should receive welcome message
```

### 2. Test Database
```bash
docker-compose exec db psql -U glyph -d glyphforge -c \
  "SELECT name, token_count FROM glyphs WHERE is_featured = TRUE LIMIT 3;"
```

### 3. Test n8n Webhook
```bash
curl -X POST http://localhost:5678/webhook/glyph-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","user_id":123,"glyph_id":1}'
```

### 4. Test Redis
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

---

## 🔄 Management Commands

### Start/Stop
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove everything (including data!)
docker-compose down -v  # WARNING: Deletes database!
```

### Restart Services
```bash
# Restart everything
docker-compose restart

# Restart specific service
docker-compose restart glyph-bot
docker-compose restart db
docker-compose restart n8n
```

### View Logs
```bash
# Follow all logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f glyph-bot
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U glyph glyphforge > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251004.sql | docker-compose exec -T db psql -U glyph glyphforge
```

---

## 📊 Monitoring

### Check Resource Usage
```bash
# See container stats
docker stats

# See disk usage
docker system df
```

### Database Stats
```bash
docker-compose exec db psql -U glyph -d glyphforge -c \
  "SELECT * FROM v_daily_activity ORDER BY activity_date DESC LIMIT 7;"
```

### Check n8n Executions
- Open n8n dashboard: `http://YOUR_IP:5678`
- Click "Executions" in sidebar
- View workflow run history

---

## 🐛 Troubleshooting

### Bot Not Responding
```bash
# Check logs
docker-compose logs glyph-bot

# Common issues:
# 1. Wrong TELEGRAM_BOT_TOKEN in .env
# 2. Bot not started with /start in Telegram
# 3. Firewall blocking connection

# Restart bot
docker-compose restart glyph-bot
```

### Database Connection Failed
```bash
# Check database is healthy
docker-compose ps db

# Check logs
docker-compose logs db

# Try connecting manually
docker-compose exec db psql -U glyph -d glyphforge
```

### n8n Not Accessible
```bash
# Check if port 5678 is open
netstat -an | grep 5678

# On Windows RDP, allow port in firewall:
New-NetFirewallRule -DisplayName "n8n" -Direction Inbound -LocalPort 5678 -Protocol TCP -Action Allow

# Check logs
docker-compose logs n8n
```

### Out of Memory
```bash
# Check memory usage
docker stats

# Add resource limits to docker-compose.yml:
services:
  glyph-bot:
    mem_limit: 512m
  db:
    mem_limit: 1g
```

### Port Already in Use
```bash
# Find what's using the port
# Linux/Mac:
lsof -i :5432

# Windows:
netstat -ano | findstr :5432

# Change port in docker-compose.yml:
ports:
  - "5433:5432"  # Use different external port
```

---

## 🔒 Security Checklist

### Before Going Live:
- [ ] Change n8n admin password
- [ ] Use strong database password
- [ ] Set up firewall rules
- [ ] Enable SSL/TLS (use Caddy or nginx)
- [ ] Regular backups scheduled
- [ ] Monitor logs for suspicious activity
- [ ] Don't expose database port publicly
- [ ] Keep .env file secure (never commit to git)

### Production Setup:
```bash
# Use secrets instead of plain text
# Create docker secrets
echo "your_bot_token" | docker secret create telegram_token -

# Update docker-compose.yml to use secrets
```

---

## 🎉 You're Live!

Your Glyph-It Forge is now running with:
✅ Telegram bot responding to commands
✅ PostgreSQL with 15 seeded glyphs
✅ n8n automation workflows active
✅ Redis caching ready
✅ Daily reports scheduled
✅ Achievement system enabled

### Next Steps:
1. Test bot in Telegram
2. Explore n8n workflows
3. Check database has seed data
4. Add more bot features from IMPLEMENTATION_EXAMPLES.md
5. Customize workflows in n8n
6. Invite users to test!

### Need Help?
- Check logs: `docker-compose logs -f`
- Review docs: `README.md`
- Database queries: Connect to PostgreSQL
- n8n workflows: Access dashboard at :5678

---

**🚀 Happy Forging!** ⚡✨
