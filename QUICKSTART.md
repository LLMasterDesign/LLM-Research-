# Τ{Raven} - Quick Start Guide

Get Raven up and running in 5 minutes! 🚀

## Prerequisites

- Python 3.11+
- Telegram account
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Step 1: Get Your Credentials

### Telegram Bot Token

1. Open Telegram and find [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow the prompts to create your bot
4. Save the **bot token** (looks like: `1234567890:ABCdefGHI...`)
5. Save the **bot username** (e.g., `@MyRavenBot`)

### Your Telegram User ID

1. Find [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send `/start`
3. Save your **user ID** (a number like `123456789`)

### Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Save the **API key** (starts with `sk-ant-api03-...`)

## Step 2: Automated Setup

```bash
# Clone or navigate to the Raven directory
cd telegram-command-station

# Make setup script executable
chmod +x scripts/setup.sh

# Run setup wizard
./scripts/setup.sh
```

The setup wizard will ask for:
- Telegram Bot Token
- Your Telegram User ID
- Bot Username
- Anthropic API Key
- Workspace path (default: `/workspace`)

It will automatically:
- Create `.env` file
- Install Python dependencies
- Create necessary directories
- Generate security keys

## Step 3: Start Raven

### Option A: Docker (Recommended)

```bash
make start
```

This starts:
- Raven Telegram Bot
- Redis (for sessions)
- PostgreSQL (for history)
- n8n (optional automation)

### Option B: Direct Python

```bash
make start-bot
```

Or manually:
```bash
cd telegram-bot
python main.py
```

## Step 4: Test It!

1. **Open Telegram** and find your bot (e.g., `@MyRavenBot`)

2. **Send** `/start`
   
   You should see:
   ```
   🌟 Welcome to Τ{Raven} - Telegram Command Station 🌟
   ```

3. **Try a question**:
   ```
   /ask What files are in this repository?
   ```

4. **Or just type naturally**:
   ```
   Show me the main function
   ```

## Common Commands

| What You Want | Command |
|---------------|---------|
| Ask AI a question | `/ask How does X work?` or just type your question |
| See workspace state | `/context` |
| Check git status | `/git status` |
| Read a file | `/file README.md` |
| Run a command | `/run ls -la` |
| Get help | `/help` |

## Troubleshooting

### Bot not responding?

1. **Check logs**:
   ```bash
   make logs-bot
   ```

2. **Verify bot is running**:
   ```bash
   make status
   ```

3. **Check .env file**:
   ```bash
   cat .env | grep TOKEN
   ```

### "Unauthorized" message?

- Make sure your Telegram User ID is in `TELEGRAM_ALLOWED_USERS` in `.env`
- Restart the bot: `make restart`

### AI not responding?

- Verify Anthropic API key is correct
- Check API quota at [Anthropic Console](https://console.anthropic.com/)
- Look for errors in logs: `make logs-bot`

### Git commands not working?

- Ensure workspace is a git repository
- Check `WORKSPACE_PATH` in `.env` points to correct directory

## Next Steps

### 🎨 Customize Behavior

Edit `.env` to adjust:
- `AI_MODEL` - Use different Claude models
- `AI_TEMPERATURE` - Control response creativity (0.0 - 1.0)
- `MAX_REQUESTS_PER_MINUTE` - Rate limiting

### 🔧 Add More Users

Edit `.env` and add user IDs (comma-separated):
```bash
TELEGRAM_ALLOWED_USERS=123456789,987654321,555555555
```

### 📊 Use n8n Workflows

1. Start with n8n: `make start`
2. Open http://localhost:5678
3. Import workflows from `n8n-workflows/`
4. Configure credentials
5. Activate workflows

### 🌐 Add Web Interface

```bash
make start-web
```

Access at http://localhost:3000

### 🚀 Deploy to Production

```bash
make deploy
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup.

## Useful Commands

```bash
make help         # Show all commands
make logs         # View all logs
make logs-bot     # View bot logs only
make status       # Check service status
make health       # Run health checks
make stop         # Stop all services
make restart      # Restart services
make clean        # Clean up everything
```

## Advanced Usage

### Multiple Workspaces

Set different workspace paths per session (coming soon)

### Voice Commands

Send voice messages to Telegram (auto-converted to text)

### File Editing

```
/file src/main.py
# Bot shows file content

# To edit (in next message):
/file src/main.py def new_function(): return True
```

### Git Workflow

```
/git status
/git diff
/git add .
/git commit -m "Your message"
/git push
```

### Complex Queries

```
/ask Analyze all Python files and find potential bugs

/ask Explain the architecture of this project

/ask Suggest performance improvements
```

## Getting Help

- **Documentation**: See [README.md](README.md) and [RAVEN_ARCHITECTURE.md](RAVEN_ARCHITECTURE.md)
- **Commands**: Send `/help` to bot
- **Logs**: Run `make logs-bot`

## Security Notes

- Never commit `.env` file
- Never share your API keys
- Review commands before confirming (especially `/run`)
- Keep `TELEGRAM_ALLOWED_USERS` restricted

---

**You're all set! Start building with Raven! 🎉**

Try asking: *"What can you help me build today?"*
