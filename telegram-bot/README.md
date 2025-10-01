# Τ{Raven} Telegram Bot

The core Telegram bot implementation for Raven Command Station.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp ../.env.example ../.env
nano ../.env
```

Required variables:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)
- `TELEGRAM_ALLOWED_USERS` - Your Telegram user ID (get from [@userinfobot](https://t.me/userinfobot))

### 3. Run the Bot

```bash
python main.py
```

Or with Docker:

```bash
docker build -t raven-bot .
docker run --env-file ../.env raven-bot
```

## Architecture

```
telegram-bot/
├── main.py                 # Entry point, bot initialization
├── handlers/
│   └── commands.py         # Command handlers (/ask, /git, etc.)
├── services/
│   ├── ai_bridge.py        # Claude API integration
│   ├── git_manager.py      # Git operations
│   └── context_tracker.py  # Workspace context management
├── models/
│   └── session.py          # Session and conversation models
└── requirements.txt        # Python dependencies
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot |
| `/help` | Show help message |
| `/ask <question>` | Ask AI about code |
| `/context` | Show workspace state |
| `/git <command>` | Execute git commands |
| `/file <path>` | Read/write files |
| `/run <command>` | Execute shell commands |
| `/session <action>` | Manage session |

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Environment Variables

See `.env.example` for all available configuration options.

## Security

- User authentication via `TELEGRAM_ALLOWED_USERS`
- Command validation and sanitization
- Rate limiting (configurable)
- Path traversal protection
- Secure API key storage

## Troubleshooting

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is running: `ps aux | grep main.py`
- Check logs: `tail -f logs/raven.log`

### AI responses failing
- Verify `ANTHROPIC_API_KEY` is valid
- Check API quota/limits
- Review error logs

### Git commands not working
- Ensure workspace is a git repository
- Check file permissions
- Verify `WORKSPACE_PATH` is correct

## Contributing

This bot is designed to be extended. Key extension points:

1. **New Commands**: Add to `handlers/commands.py`
2. **New Services**: Create in `services/`
3. **Custom Context**: Extend `ContextTracker`
4. **Session Storage**: Implement Redis/PostgreSQL backend

## License

MIT
