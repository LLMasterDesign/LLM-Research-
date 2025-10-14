# 🦉 NOCTUA - The Owl Continuity Agent

**Local-first continuity agent with Redis backend, Telegram integration, and n8n-inspired dashboard**

Built by: Lucius Larz Master (RAVEN CODEX)  
License: AGPL-3.0-or-later

---

## 🎯 What is NOCTUA?

NOCTUA (The Owl) is a **local-first continuity agent** designed to provide:

- **🔒 Identity**: Cryptographically unique NodeID for each instance
- **💾 Memory**: Persistent key-value storage with SQLite + optional Redis
- **📜 History**: Complete conversation and event logging
- **🧩 Folder Blocks**: n8n-inspired visual workflow system with floating folder nodes
- **💬 Telegram**: Mobile access through Telegram bot integration
- **🌐 Dashboard**: Beautiful web UI for managing workflows and data
- **♻️ Continuity**: Restart-proof operation with automatic backups

---

## 🚀 Quick Start

### 1. Build NOCTUA

```bash
# Run the builder (creates .3ox structure)
python3 build_noctua.py
```

### 2. Launch the Owl

```bash
# Interactive mode
python3 .3ox/owl.py

# Background daemon mode
python3 .3ox/owl.py --daemon
```

### 3. Open the Dashboard

```bash
# Install optional dependencies first
pip install flask flask-cors

# Start dashboard
python3 .3ox/dashboard.py
```

Then open: **http://localhost:8080**

---

## 📦 Installation

### Basic Installation (SQLite only)

```bash
pip install tomli  # For Python < 3.11
```

### Full Installation (All features)

```bash
pip install -r requirements.txt
```

This includes:
- ✅ Redis support for distributed continuity
- ✅ Flask dashboard with n8n-style UI
- ✅ Telegram bot integration

---

## 🏗️ Architecture

### Directory Structure

```
.3ox/
├── config.toml          # Configuration
├── !3ox.key            # Cryptographic identity key
├── manifest.toml       # System manifest
├── noctua.db          # SQLite database
├── 3ox.log            # Operation logs
├── owl.py             # Core continuity daemon
├── dashboard.py       # Web dashboard
├── telegram_bot.py    # Telegram integration
└── backups/           # Automatic database backups
```

### Database Schema

**Memory Table** (`mem`)
- Persistent key-value store
- Node-scoped for multi-agent support
- Synced to Redis when available

**History Table** (`history`)
- Complete event and conversation log
- Timestamped with role and content
- Streamed to Redis for real-time access

**Folder Blocks Table** (`folder_blocks`)
- Visual workflow nodes (n8n-style)
- Each block represents a folder/process
- Drag-and-drop positioning stored
- JSON config for extensibility

---

## 🎨 Dashboard Features

The NOCTUA Dashboard is inspired by **n8n** with a modern dark theme:

### Visual Workflow Editor
- 🧩 **Floating Folder Blocks** - Each block represents a folder/process
- 🎯 **Drag & Drop** - Move blocks around the canvas
- 🔗 **Connections** - Link blocks to create workflows
- 📊 **Real-time Stats** - Live memory, history, and block counts

### Block Types
- ⚙️ **Config** - Configuration management
- 📦 **Data** - Data processing nodes
- ✅ **Task** - Task execution blocks
- 💬 **Telegram** - Bot integration nodes

### Screenshots
*(Dashboard runs at http://localhost:8080)*

---

## 💬 Telegram Integration

### Setup

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Edit `.3ox/config.toml`:

```toml
[telegram]
enabled = true
token = "YOUR_BOT_TOKEN_HERE"
allowed_users = [123456789]  # Optional: restrict access
```

4. Launch the bot:

```bash
python3 .3ox/telegram_bot.py
```

### Available Commands

- `/start` - Initialize bot
- `/status` - Show system status
- `/memory` - List recent memory keys
- `/set <key> <value>` - Store memory
- `/get <key>` - Retrieve memory
- `/blocks` - List folder blocks
- `/help` - Show help

---

## 🔴 Redis Backend

For distributed continuity and multi-device sync:

### Install Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

### Enable in Config

```toml
[redis]
enabled = true
host = "localhost"
port = 6379
db = 0
prefix = "noctua:"
```

Redis provides:
- ⚡ Fast distributed memory access
- 🔄 Real-time sync across devices
- 📊 Stream-based history for dashboards

---

## 🔧 Configuration

Edit `.3ox/config.toml` to customize:

```toml
[persona]
name = "NOCTUA"
postscript = "🦉"
identity = "The Owl - Local-first Continuity Agent"

[continuity]
db_path = ".3ox/noctua.db"
log_path = ".3ox/3ox.log"
key_path = ".3ox/!3ox.key"
autobackup = true
rotation_days = 7

[redis]
enabled = true
host = "localhost"
port = 6379

[telegram]
enabled = false
token = ""

[dashboard]
enabled = true
host = "localhost"
port = 8080
style = "n8n"
floating_folders = true
```

---

## 🧪 API Usage

### Python API

```python
from owl import NoctuaOwl

# Initialize
owl = NoctuaOwl()

# Store memory
owl.set_memory("user_name", "Lucius")

# Retrieve memory
name = owl.get_memory("user_name")

# Log history
owl.log_history("user", "Hello NOCTUA!")

# Create folder block
block_id = owl.create_folder_block(
    folder_path="/workspace/project",
    block_type="config",
    config={"name": "Project Config"},
    position=(100, 100)
)

# Get all blocks
blocks = owl.get_folder_blocks()

# Manual backup
owl.backup()

# Clean shutdown
owl.shutdown()
```

---

## 🔐 Security

- **Cryptographic Identity**: Each NOCTUA instance has a unique NodeID derived from a secure key
- **Key Storage**: The `.3ox/!3ox.key` file should be kept secret
- **Telegram Auth**: Optional user allowlist for bot access
- **Local-First**: All data stored locally, Redis is optional

---

## 🚀 Deployment Options

### 1. Local Development
```bash
python3 .3ox/owl.py
```

### 2. Background Daemon
```bash
# Run as daemon
python3 .3ox/owl.py --daemon

# Or use systemd
sudo systemctl enable noctua
sudo systemctl start noctua
```

### 3. Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY .3ox /app/.3ox
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["python", ".3ox/owl.py", "--daemon"]
```

### 4. Cursor Integration
NOCTUA can run as a background agent in Cursor IDE:
- Maintains continuity across sessions
- Stores project context and memory
- Integrates with .3ox folder structure

---

## 📊 Monitoring

### Check Logs
```bash
tail -f .3ox/3ox.log
```

### Database Stats
```bash
sqlite3 .3ox/noctua.db "SELECT COUNT(*) FROM mem"
sqlite3 .3ox/noctua.db "SELECT COUNT(*) FROM history"
sqlite3 .3ox/noctua.db "SELECT COUNT(*) FROM folder_blocks"
```

### Redis Stats (if enabled)
```bash
redis-cli
> KEYS noctua:*
> GET noctua:mem:NODE_ID:KEY
```

---

## 🛠️ Development

### Project Structure
```
/workspace/
├── build_noctua.py      # Builder script
├── requirements.txt     # Dependencies
└── .3ox/               # NOCTUA installation
    ├── owl.py          # Core daemon
    ├── dashboard.py    # Web UI
    ├── telegram_bot.py # Bot integration
    └── noctua.db       # Data storage
```

### Extending NOCTUA

Add new block types in `dashboard.py`:
```python
# Custom block type
block_types = {
    'custom': '🎨',
    # ... existing types
}
```

Add custom commands to Telegram bot:
```python
async def cmd_custom(self, update, context):
    # Your custom command
    pass

self.app.add_handler(CommandHandler("custom", self.cmd_custom))
```

---

## 🐛 Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG
```

### Telegram Bot Not Starting
```bash
# Verify token in config.toml
cat .3ox/config.toml | grep token

# Test token manually
curl https://api.telegram.org/bot<TOKEN>/getMe
```

### Dashboard Not Loading
```bash
# Check if Flask is installed
pip show flask

# Verify port is not in use
lsof -i :8080
```

---

## 📝 Manifest System

NOCTUA uses a TOML-based manifest for deployment:

```toml
[manifest]
id = "NOCTUA"
node_id = "e4a8da0b1ebaf6e6683f238b3e06ed55..."
version = "1.0.0"

[capabilities]
continuity = true
memory = true
redis_backend = true
telegram_integration = true
dashboard = true
folder_blocks = true

[runtime]
python_version = "3.10+"
launch_command = "python .3ox/owl.py"
mode = "background"
restart_on_crash = true
```

---

## 🎯 Use Cases

### 1. Personal Knowledge Base
- Store notes, ideas, and references
- Access via Telegram on mobile
- Visualize connections in dashboard

### 2. Project Continuity
- Maintain context across coding sessions
- Store project-specific memory
- Track task history

### 3. Multi-Device Sync
- Redis backend for distributed access
- Telegram bot for mobile interface
- Web dashboard for desktop

### 4. Workflow Automation
- n8n-style visual workflows
- Folder-based process blocks
- Extensible with custom types

---

## 🤝 Contributing

NOCTUA is built with the RAVEN CODEX philosophy:
- **Local-first**: Data sovereignty and privacy
- **Restart-proof**: Continuity across sessions
- **Extensible**: Plugin-based architecture
- **Beautiful**: Modern UI/UX principles

---

## 📄 License

AGPL-3.0-or-later

---

## 🦉 About the Owl

> "The owl sees in the dark, remembers through sleep, and awakens with continuity intact."

NOCTUA embodies:
- 🌙 **Night vision**: Operates in background
- 🧠 **Memory**: Never forgets context
- 🔄 **Continuity**: Survives restarts
- 🦉 **Wisdom**: Learns from history

---

## 🚀 Next Steps

1. **Build**: `python3 build_noctua.py`
2. **Launch**: `python3 .3ox/owl.py`
3. **Explore**: Open dashboard at http://localhost:8080
4. **Extend**: Add custom blocks and integrations

**NOCTUA is ready.** 🦉

---

*Built with 🦉 by Lucius Larz Master*  
*Part of the RAVEN CODEX project*

:: ∎
