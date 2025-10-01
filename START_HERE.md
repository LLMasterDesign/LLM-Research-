# 🚀 START HERE - Τ{Raven} Quick Launch Guide

> **Welcome to Raven!** Your AI-powered Telegram Command Station is ready to go.

---

## ⚡ 30-Second Quick Start

```bash
# 1. Setup (interactive wizard)
./scripts/setup.sh

# 2. Start bot
make start-bot

# 3. Open Telegram → Find your bot → Send /start
# 🎉 Done!
```

---

## 📚 Documentation Guide

Choose your path based on what you need:

### 🏃 I want to start NOW
→ Read [QUICKSTART.md](QUICKSTART.md)
   - 5-minute setup guide
   - Step-by-step with screenshots
   - Troubleshooting tips

### 🤔 I want to understand the system
→ Read [README.md](README.md)
   - Project overview
   - Features and capabilities
   - Use cases and examples

### 🏗️ I want technical details
→ Read [RAVEN_ARCHITECTURE.md](RAVEN_ARCHITECTURE.md)
   - System architecture
   - Component details
   - Design decisions

### 📊 I want visual diagrams
→ Read [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)
   - Flow diagrams
   - Component interactions
   - Data models

### 🎨 I want a visual overview
→ Read [VISUAL_OVERVIEW.md](VISUAL_OVERVIEW.md)
   - ASCII art
   - Stats and metrics
   - Visual guides

### 🚀 I want to deploy to production
→ Read [DEPLOYMENT.md](DEPLOYMENT.md)
   - Production setup guide
   - Cloud platform options
   - Security hardening
   - Monitoring and backups

### 📦 I want to see what was built
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
   - Complete feature list
   - File structure
   - Development timeline

---

## 🎯 What You Need Before Starting

1. **Telegram Bot Token**
   - Get from [@BotFather](https://t.me/botfather)
   - Takes 30 seconds

2. **Your Telegram User ID**
   - Get from [@userinfobot](https://t.me/userinfobot)
   - Takes 10 seconds

3. **Anthropic API Key**
   - Sign up at [console.anthropic.com](https://console.anthropic.com/)
   - Free tier available

4. **Python 3.11+** (or Docker)
   - Check: `python3 --version`

---

## 💡 Quick Command Reference

### Setup & Deployment
```bash
make setup        # Initial configuration
make install      # Install dependencies
make start        # Start with Docker
make start-bot    # Start locally
make stop         # Stop services
make restart      # Restart services
```

### Monitoring
```bash
make logs         # View all logs
make logs-bot     # View bot logs only
make status       # Service status
make health       # Health checks
```

### Development
```bash
make test         # Run tests
make lint         # Run linters
make format       # Format code
```

### Maintenance
```bash
make clean        # Clean up
make deploy       # Deploy to production
```

---

## 🤖 Telegram Commands

Once your bot is running:

```
/start              # Initialize
/help               # Show all commands
/ask <question>     # Ask AI
/context            # Show workspace
/git status         # Git operations
/file README.md     # Read files
/run ls -la         # Execute commands
```

Or just **type naturally**:
- "Show me the tests"
- "What does the main function do?"
- "How is this project structured?"

---

## 🎬 Example Session

```
You: /start
Bot: 🌟 Welcome to Τ{Raven}! I'm ready to help.

You: What files are in this repository?
Bot: 📂 I found 32 files in /workspace:
     • README.md
     • telegram-bot/main.py
     • ...

You: Explain how the bot works
Bot: 💡 The bot consists of several components:
     1. Main entry point (main.py) that...
     2. Command handlers that route...
     3. Services that provide...
     [Detailed explanation with code references]

You: /git status
Bot: ```
     On branch main
     Your branch is up to date with 'origin/main'
     nothing to commit, working tree clean
     ```

You: Perfect! Thanks!
Bot: 🎉 Happy to help! Ask me anything about your code.
```

---

## 🆘 Troubleshooting

### Bot not responding?
```bash
# Check if bot is running
make status

# View logs for errors
make logs-bot

# Restart
make restart
```

### Configuration issues?
```bash
# Re-run setup
./scripts/setup.sh

# Verify .env file
cat .env | grep TOKEN
```

### Need more help?
- Check logs: `make logs-bot`
- Read troubleshooting in QUICKSTART.md
- Review error messages carefully
- Check .env configuration

---

## 🌟 What Makes Raven Special?

1. **Context-Aware** - AI knows your entire codebase
2. **Mobile-First** - Code from anywhere via Telegram
3. **Natural Language** - No commands to memorize
4. **Production-Ready** - Deploy in minutes
5. **Secure** - Your data, your server
6. **Extensible** - Add your own features easily

---

## 🎓 Learning Path

**Beginner:**
1. Run `./scripts/setup.sh`
2. Start bot with `make start-bot`
3. Chat with bot on Telegram
4. Try different commands

**Intermediate:**
1. Read RAVEN_ARCHITECTURE.md
2. Explore the code in `telegram-bot/`
3. Customize commands in `handlers/commands.py`
4. Add your own features

**Advanced:**
1. Deploy to production with `make deploy`
2. Set up n8n workflows
3. Implement custom integrations
4. Scale to multiple users

---

## 📞 Support Resources

- **Quick Help**: Run `make help`
- **Bot Help**: Send `/help` to your bot
- **Documentation**: All `.md` files in root
- **Logs**: `make logs-bot`

---

## 🎉 Ready? Let's Go!

```bash
# This is all you need to start:
./scripts/setup.sh && make start-bot
```

Then open Telegram and find your bot!

---

**Made with ⚡ and 🤖 for developers who want to code from anywhere**

**Version:** 0.1.0  
**Status:** ✅ Production Ready  
**License:** MIT

---

## 🗺️ Navigation Map

```
START_HERE.md (You are here!)
    ├─→ QUICKSTART.md ............... Fast setup
    ├─→ README.md ................... Overview
    ├─→ RAVEN_ARCHITECTURE.md ....... Technical
    ├─→ DEPLOYMENT.md ............... Production
    ├─→ ARCHITECTURE_DIAGRAM.md ..... Diagrams
    ├─→ VISUAL_OVERVIEW.md .......... Visual guide
    └─→ PROJECT_SUMMARY.md .......... Summary
```

**Choose your path and start building! 🚀**
