# Τ{Raven} n8n Workflows

Pre-built n8n workflow templates for Raven automation.

## What is n8n?

[n8n](https://n8n.io) is a fair-code licensed workflow automation platform that allows you to connect different services and create automated workflows visually.

## Available Workflows

### 1. Telegram AI Bridge (`telegram-ai-bridge.json`)

Main workflow that connects Telegram to Claude AI.

**Features:**
- Receives messages from Telegram
- Routes commands appropriately
- Queries Claude AI with context
- Executes git commands
- Sends formatted responses back

**Nodes:**
- Telegram Trigger
- Command Router (IF conditions)
- Claude AI HTTP Request
- Git Command Executor
- Response Formatter

### 2. Git Operations (`git-operations.json`) - Coming Soon

Dedicated workflow for advanced git operations.

### 3. File Manager (`file-manager.json`) - Coming Soon

File browsing, searching, and editing workflow.

## Setup Instructions

### Prerequisites

1. **n8n Installation**
   ```bash
   # Option 1: Docker
   docker run -it --rm \
     --name n8n \
     -p 5678:5678 \
     -v ~/.n8n:/home/node/.n8n \
     n8nio/n8n
   
   # Option 2: npm
   npm install -g n8n
   n8n start
   ```

2. **Access n8n**
   - Open http://localhost:5678
   - Create an account

### Import Workflows

1. **Open n8n dashboard** (http://localhost:5678)
2. Click **"Import from File"** or **"Import from URL"**
3. Select the workflow JSON file from this directory
4. Click **"Import"**

### Configure Credentials

#### Telegram Bot API
1. Get bot token from [@BotFather](https://t.me/botfather)
2. In n8n, go to **Credentials** → **New** → **Telegram API**
3. Enter your bot token
4. Save

#### Anthropic API
1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. In n8n, go to **Credentials** → **New** → **HTTP Header Auth**
3. Name: `x-api-key`
4. Value: Your Anthropic API key
5. Save

### Activate Workflows

1. Open the imported workflow
2. Review and update any workspace paths
3. Click **"Active"** toggle in top right
4. Test by sending a message to your Telegram bot

## Workflow Architecture

```
[Telegram Message]
        ↓
[Telegram Trigger Node]
        ↓
[Command Router (IF)]
        ↓
   ┌────┴────┐
   ↓         ↓
[/ask]    [/git]
   ↓         ↓
[AI Query] [Git Exec]
   ↓         ↓
[Response Format]
   ↓
[Send to Telegram]
```

## Customization

### Adding New Commands

1. Open workflow in n8n
2. Add new **IF node** for command detection
3. Add processing nodes for command logic
4. Connect to response node

Example:
```javascript
// In IF node condition
{{$json["message"]["text"]}} starts with "/mycommand"

// In Code node
const command = $input.item.json.message.text;
const result = processMyCommand(command);
return { result };
```

### Modifying AI Behavior

Edit the **Ask Claude AI** node:
- Change `model` parameter for different Claude versions
- Adjust `max_tokens` for longer/shorter responses
- Modify `system` prompt for different behavior

### Adding Context Awareness

Add nodes to:
1. Read workspace files
2. Execute git commands
3. Build context string
4. Inject into AI prompt

## Advanced Features

### Webhooks

Replace Telegram Trigger with Webhook node for custom integrations:

```javascript
// Webhook URL: https://your-n8n.com/webhook/raven
// POST body:
{
  "question": "Your question here",
  "user_id": "123456",
  "context": {...}
}
```

### Scheduled Tasks

Add **Cron node** for automated tasks:
- Daily git status reports
- Code quality checks
- Dependency updates

### Multi-User Support

Add **Function node** to manage user sessions:
```javascript
// Store user context
const userId = $json.message.from.id;
const userState = $workflow.getStaticData(userId);

// Use stored context in AI queries
```

## Troubleshooting

### Workflow not triggering
- Check bot token is correct
- Verify webhook URL is accessible
- Check n8n is running and active

### AI responses failing
- Verify Anthropic API key
- Check API rate limits
- Review error logs in n8n

### Git commands not working
- Ensure n8n has file system access
- Check workspace path is correct
- Verify git is installed in n8n container

## Performance Optimization

1. **Use async execution** - Enable in workflow settings
2. **Cache AI responses** - Add Redis node
3. **Rate limiting** - Add throttle nodes
4. **Error handling** - Add error workflows

## Security

- **Never expose credentials** in workflow JSON
- **Validate user input** before executing commands
- **Use environment variables** for sensitive data
- **Implement access control** in IF nodes

## Migration from Python Bot

n8n workflows can run alongside the Python bot or replace it:

**Advantages of n8n:**
- Visual workflow design
- Built-in integrations
- Easy to modify
- Cloud hosting available

**Advantages of Python bot:**
- More control
- Better for complex logic
- Easier debugging
- Custom extensions

**Hybrid approach:**
- Use n8n for simple commands
- Use Python bot for complex AI interactions
- Share Redis for session state

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Anthropic API](https://docs.anthropic.com/)

## Contributing

To contribute new workflows:
1. Create workflow in n8n
2. Export as JSON
3. Document in this README
4. Test thoroughly
5. Submit PR

## License

MIT
