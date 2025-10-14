# NOCTUA Project Structure

## Overview
NOCTUA (The Owl) - A local-first continuity agent with Redis backend, Telegram integration, and n8n-inspired dashboard.

## Files Created

### Core System
- `build_noctua.py` - Builder script that creates and initializes NOCTUA
- `requirements.txt` - Python dependencies (tomli, redis, flask, telegram)
- `deploy.sh` - Quick deployment helper script

### .3ox Directory (NOCTUA Installation)
- `.3ox/owl.py` - Core continuity daemon with SQLite + Redis support
- `.3ox/dashboard.py` - Web-based n8n-inspired UI with floating folder blocks
- `.3ox/telegram_bot.py` - Telegram bot integration for mobile access
- `.3ox/config.toml` - Configuration file
- `.3ox/!3ox.key` - Cryptographic identity key (32-char hex)
- `.3ox/manifest.toml` - System manifest with NodeID and capabilities
- `.3ox/noctua.db` - SQLite database (3 tables: mem, history, folder_blocks)
- `.3ox/3ox.log` - Operation logs
- `.3ox/backups/` - Automatic database backups

### Documentation
- `NOCTUA_README.md` - Complete documentation and usage guide

## Architecture

### Database Schema
1. **mem** - Key-value memory store (node-scoped)
2. **history** - Event and conversation log
3. **folder_blocks** - Visual workflow nodes (n8n-style)

### Components
1. **owl.py** - Core daemon
   - Memory persistence (SQLite + Redis)
   - History logging
   - Folder block management
   - Automatic backups
   - NodeID cryptographic identity

2. **dashboard.py** - Web UI
   - n8n-inspired dark theme
   - Floating folder blocks (drag & drop)
   - Real-time stats
   - Block types: config, data, task, telegram
   - Runs on localhost:8080

3. **telegram_bot.py** - Mobile interface
   - Commands: /start, /status, /memory, /set, /get, /blocks
   - User authorization
   - History logging
   - Memory access

### Features
- ✅ Local-first architecture
- ✅ Restart-proof continuity
- ✅ Cryptographic identity (NodeID)
- ✅ SQLite + optional Redis backend
- ✅ Beautiful web dashboard
- ✅ Telegram mobile access
- ✅ n8n-style visual workflows
- ✅ Automatic backups
- ✅ Multi-device sync (Redis)

## Usage

### Quick Start
```bash
# Deploy NOCTUA
./deploy.sh

# Or manually:
python3 build_noctua.py
python3 .3ox/owl.py
```

### Dashboard
```bash
pip install flask flask-cors
python3 .3ox/dashboard.py
# Open: http://localhost:8080
```

### Telegram
```bash
# 1. Edit .3ox/config.toml - add bot token
# 2. Launch bot
pip install python-telegram-bot
python3 .3ox/telegram_bot.py
```

## Configuration
All settings in `.3ox/config.toml`:
- Persona and identity
- Database paths
- Redis connection
- Telegram settings
- Dashboard options

## NodeID
Unique cryptographic identity:
`e4a8da0b1ebaf6e6683f238b3e06ed554e9deb73d1b48c3e0f0dd26dcfb9738f`

Derived from `.3ox/!3ox.key` using HMAC-SHA256

## Status
✅ NOCTUA built and deployed successfully
- 1 folder block created (sample)
- 1 memory key stored (boot_time)
- 1 history item logged (system startup)
- Database initialized with all tables
- All modules created and executable

## Next Steps
1. Install optional dependencies: `pip install -r requirements.txt`
2. Start dashboard: `python3 .3ox/dashboard.py`
3. Configure Telegram (optional): Edit `.3ox/config.toml`
4. Enable Redis (optional): Install and start redis-server

## Built by
Lucius Larz Master (RAVEN CODEX)
License: AGPL-3.0-or-later

:: ∎
