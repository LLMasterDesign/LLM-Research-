# Τ{Raven} - Telegram Command Station

> **Transform Telegram into your personal AI-powered development command center**

[![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**🚀 NEW HERE? [START HERE](START_HERE.md) for quick setup!**

---

## 🎯 What is Raven?

**Τ{Raven}** is a seamless bridge between Telegram and Cursor AI, allowing you to interact with this powerful AI development environment through simple Telegram messages. Think of it as your personal AI assistant that has full context of your codebase, git history, and development environment - accessible from anywhere via Telegram.

### Why Raven?

- 🚀 **Instant Access**: Ask questions, execute commands, and manage code from your phone
- 🧠 **Full Context**: AI understands your entire workspace, not just isolated questions
- 🔄 **Bidirectional**: Send commands and receive rich, formatted responses
- 🛡️ **Secure**: Encrypted communication, authenticated access
- ⚡ **Fast**: Low-latency responses optimized for mobile interaction

---

## 🏗️ Architecture

Raven supports multiple implementation pathways:

1. **Python Bot + Cursor Bridge** (Primary) - Direct, fast, full control
2. **n8n Automation** - Visual workflows, easy customization
3. **Telegram Mini App** - Rich web UI embedded in Telegram
4. **RDP Bridge** - Full desktop access for visual tasks

See [RAVEN_ARCHITECTURE.md](RAVEN_ARCHITECTURE.md) for detailed technical documentation.

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token ([Get one from @BotFather](https://t.me/botfather))
- Anthropic API Key (for Claude AI)
- Docker & Docker Compose (optional, recommended)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd telegram-command-station

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Option 1: Docker Compose (Recommended)
docker-compose up -d

# Option 2: Local Development
cd telegram-bot
pip install -r requirements.txt
python main.py
```

### First Interaction

1. Open Telegram and find your bot (@YourBotName)
2. Send `/start` to initialize
3. Try `/ask What files are in this repository?`
4. Experience the magic! ✨

---

## 🎮 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialize bot and create session | `/start` |
| `/ask <question>` | Ask AI anything about your code | `/ask Explain this function` |
| `/context` | Show current workspace state | `/context` |
| `/git <command>` | Execute git operations | `/git status` |
| `/file <path>` | Read or edit files | `/file src/main.py` |
| `/run <command>` | Execute shell commands | `/run npm test` |
| `/session` | Manage conversation sessions | `/session reset` |
| `/help` | Show all available commands | `/help` |

---

## 📦 Project Structure

```
Τ{Raven}/
├── telegram-bot/          # Core bot server (Python)
├── cursor-bridge/         # AI integration layer
├── n8n-workflows/         # Automation templates
├── web-interface/         # Optional web UI
├── infra/                 # Infrastructure configs
└── scripts/               # Deployment utilities
```

---

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=your_telegram_user_id

# AI Configuration
ANTHROPIC_API_KEY=your_claude_api_key
AI_MODEL=claude-sonnet-4

# Workspace Configuration
WORKSPACE_PATH=/workspace
GIT_REPO_PATH=/workspace

# Database (Optional)
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:pass@localhost/raven

# Security
SECRET_KEY=generate_a_random_secret_key
MAX_REQUESTS_PER_MINUTE=20
```

---

## 🌟 Features

### Current Features
- ✅ Basic Telegram bot interface
- ✅ Git repository context awareness
- ✅ AI conversation with full workspace context
- ✅ File operations (read, search)
- ✅ Command execution with safety checks

### Coming Soon
- 🚧 Session persistence across restarts
- 🚧 Multi-workspace support
- 🚧 n8n workflow templates
- 🚧 Web interface (Telegram Mini App)
- 🚧 Voice command support
- 🚧 Collaborative mode
- 🚧 Advanced git operations (merge, rebase, PR creation)

---

## 🛠️ Development

### Running Tests

```bash
cd telegram-bot
pytest tests/ -v
```

### Building Docker Image

```bash
docker build -t raven-telegram-bot ./telegram-bot
```

### Contributing

Contributions welcome! This project is designed to evolve based on real-world usage patterns.

---

## 🔐 Security

- All API keys are stored securely in environment variables
- User authentication via Telegram user IDs
- Command validation and sanitization
- Rate limiting to prevent abuse
- Audit logging for all operations

**Note**: Never commit your `.env` file or expose API keys publicly.

---

## 📚 Documentation

- [Architecture Overview](RAVEN_ARCHITECTURE.md)
- [Bot Setup Guide](telegram-bot/README.md)
- [n8n Workflows](n8n-workflows/README.md)
- [API Reference](docs/API.md) *(coming soon)*

---

## 🤝 Use Cases

1. **Mobile Development**: Code review and quick fixes from your phone
2. **Quick Queries**: "What does this function do?" while away from desk
3. **Git Operations**: Check status, create branches, merge PRs
4. **CI/CD Monitoring**: Get build notifications and logs
5. **Team Collaboration**: Share workspace access with team members
6. **Learning**: Ask questions about unfamiliar codebases

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Anthropic Claude API](https://www.anthropic.com/)
- [n8n](https://n8n.io/) (optional automation)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/raven/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/raven/discussions)
- **Telegram**: @YourSupportChannel

---

**Made with ⚡ by autonomous AI agents**
