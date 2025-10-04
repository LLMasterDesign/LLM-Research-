# Glyph-It Forge - Quick Start Guide
## Get Your Telegram Prompt Bot Running in 30 Minutes

---

## 🎯 What We're Building

A Telegram bot that lets users:
- ✅ Create custom prompts ("glyphs") under 27 tokens
- ✅ Store and organize their prompt library
- ✅ Track usage statistics
- ✅ Browse and share glyphs
- ✅ Mix glyphs to create new ones

---

## 📋 Prerequisites

```bash
# Check you have these installed:
python --version  # Python 3.10+
docker --version  # Docker 20+
git --version     # Git 2.30+
```

---

## 🚀 Step 1: Create Your Bot (5 minutes)

### 1.1 Talk to BotFather on Telegram

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name: `Glyph Forge`
4. Choose a username: `your_glyph_forge_bot`
5. **Save the token** BotFather gives you!

### 1.2 Set Up Bot Commands

Send to BotFather:
```
/setcommands

Then paste:
start - Start the bot
forge - Create a new glyph
list - View your glyphs
stats - See your statistics
mix - Combine two glyphs
help - Show help
```

---

## 🏗️ Step 2: Project Setup (5 minutes)

```bash
# Create project directory
mkdir glyph-forge-bot
cd glyph-forge-bot

# Create directory structure
mkdir -p data src/{handlers,storage,utils}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
python-telegram-bot==20.7
python-dotenv==1.0.0
sqlalchemy==2.0.23
matplotlib==3.8.2
aiosqlite==0.19.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_token_from_botfather
DATABASE_URL=sqlite+aiosqlite:///data/glyphs.db
DEBUG=True
EOF

# Edit .env and add your real token
nano .env
```

---

## 💻 Step 3: Core Bot Code (10 minutes)

### 3.1 Create `src/bot.py`

```python
import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Simple in-memory storage (replace with DB later)
USER_GLYPHS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    keyboard = [
        [InlineKeyboardButton("🔨 Forge Glyph", callback_data='forge')],
        [InlineKeyboardButton("📚 My Glyphs", callback_data='list')],
        [InlineKeyboardButton("📊 Statistics", callback_data='stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌟 **Welcome to Glyph-It Forge!**\n\n"
        "Create powerful prompts under 27 tokens.\n"
        "What would you like to do?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'forge':
        await forge_menu(query, context)
    elif query.data == 'list':
        await list_glyphs(query, context)
    elif query.data == 'stats':
        await show_stats(query, context)
    elif query.data == 'help':
        await show_help(query, context)

async def forge_menu(query, context):
    """Show forge options"""
    keyboard = [
        [InlineKeyboardButton("🧠 Wisdom", callback_data='seed_wisdom')],
        [InlineKeyboardButton("⚡ Power", callback_data='seed_power')],
        [InlineKeyboardButton("⚖️ Balance", callback_data='seed_balance')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔨 **Forge a New Glyph**\n\n"
        "Choose your seed essence:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def list_glyphs(query, context):
    """List user's glyphs"""
    user_id = query.from_user.id
    glyphs = USER_GLYPHS.get(user_id, {})
    
    if not glyphs:
        keyboard = [[InlineKeyboardButton("🔨 Create First Glyph", callback_data='forge')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📚 Your library is empty!\n\nCreate your first glyph.",
            reply_markup=reply_markup
        )
        return
    
    text = "📚 **Your Glyph Library:**\n\n"
    keyboard = []
    
    for name, data in list(glyphs.items())[:10]:
        preview = data['text'][:30] + "..." if len(data['text']) > 30 else data['text']
        text += f"🔹 **{name}**\n   {preview}\n   Uses: {data['uses']}\n\n"
        keyboard.append([InlineKeyboardButton(f"📋 {name}", callback_data=f'view_{name}')])
    
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_stats(query, context):
    """Show user statistics"""
    user_id = query.from_user.id
    glyphs = USER_GLYPHS.get(user_id, {})
    
    total = len(glyphs)
    total_uses = sum(g['uses'] for g in glyphs.values()) if glyphs else 0
    avg_uses = total_uses / total if total > 0 else 0
    
    text = f"📊 **Your Statistics**\n\n"
    text += f"📚 Total Glyphs: {total}\n"
    text += f"🔥 Total Uses: {total_uses}\n"
    text += f"📈 Average Uses: {avg_uses:.1f}\n\n"
    
    if glyphs:
        sorted_glyphs = sorted(glyphs.items(), key=lambda x: x[1]['uses'], reverse=True)[:3]
        text += "🏆 **Top 3:**\n"
        for i, (name, data) in enumerate(sorted_glyphs, 1):
            text += f"{i}. {name} - {data['uses']} uses\n"
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help(query, context):
    """Show help"""
    text = (
        "❓ **Glyph-It Forge Help**\n\n"
        "**Commands:**\n"
        "/start - Open main menu\n"
        "/forge - Create a new glyph\n"
        "/list - View your glyphs\n"
        "/stats - See your statistics\n\n"
        "**What's a Glyph?**\n"
        "A glyph is a powerful, compact prompt (under 27 tokens) "
        "that you can reuse in AI conversations.\n\n"
        "**Tips:**\n"
        "• Keep glyphs focused and clear\n"
        "• Use descriptive names\n"
        "• Mix glyphs to create new ones\n"
    )
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔨 Forge Glyph", callback_data='forge')],
        [InlineKeyboardButton("📚 My Glyphs", callback_data='list')],
        [InlineKeyboardButton("📊 Statistics", callback_data='stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌟 **Glyph-It Forge**\n\nWhat would you like to do?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env!")
        return
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    logger.info("🚀 Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
```

---

## 🧪 Step 4: Test Your Bot (5 minutes)

```bash
# Make sure you're in the project directory with venv activated
python src/bot.py
```

Now open Telegram and:
1. Search for your bot (`@your_glyph_forge_bot`)
2. Send `/start`
3. You should see the menu with buttons!
4. Click around and test the interface

Press `Ctrl+C` to stop the bot.

---

## 🐳 Step 5: Dockerize (5 minutes)

### 5.1 Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env .

# Create data directory
RUN mkdir -p data

# Run bot
CMD ["python", "src/bot.py"]
```

### 5.2 Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: glyph_forge
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5.3 Build and Run

```bash
# Build the container
docker-compose build

# Run the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

---

## 🎨 Step 6: Add Your First Real Feature (Optional)

Let's add the ability to actually save a glyph!

Add this to `src/bot.py`:

```python
from telegram.ext import ConversationHandler, MessageHandler, filters

# States for conversation
GLYPH_NAME, GLYPH_TEXT = range(2)

async def forge_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start glyph creation"""
    await update.message.reply_text(
        "🔨 **Let's forge a glyph!**\n\n"
        "First, give it a name (one word, no spaces):",
        parse_mode='Markdown'
    )
    return GLYPH_NAME

async def get_glyph_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get glyph name"""
    name = update.message.text.strip().replace(' ', '_')
    context.user_data['glyph_name'] = name
    
    await update.message.reply_text(
        f"✅ Name: **{name}**\n\n"
        "Now, enter your glyph text (keep it under 27 tokens!):",
        parse_mode='Markdown'
    )
    return GLYPH_TEXT

async def get_glyph_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get glyph text and save"""
    text = update.message.text.strip()
    name = context.user_data['glyph_name']
    user_id = update.effective_user.id
    
    # Check token count (rough estimate)
    token_count = len(text.split())
    
    if token_count > 27:
        await update.message.reply_text(
            f"⚠️ Too long! ({token_count} tokens)\n"
            "Please shorten to under 27 tokens:"
        )
        return GLYPH_TEXT
    
    # Save glyph
    if user_id not in USER_GLYPHS:
        USER_GLYPHS[user_id] = {}
    
    USER_GLYPHS[user_id][name] = {
        'text': text,
        'uses': 0,
        'created': str(datetime.now())
    }
    
    await update.message.reply_text(
        f"✨ **Glyph forged successfully!**\n\n"
        f"Name: {name}\n"
        f"Tokens: {token_count}\n\n"
        f"```\n{text}\n```\n\n"
        "Use /list to see all your glyphs!",
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Cancelled. Use /start to return to menu.")
    return ConversationHandler.END

# Add to main() function:
forge_conv = ConversationHandler(
    entry_points=[CommandHandler('forge', forge_start)],
    states={
        GLYPH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_glyph_name)],
        GLYPH_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_glyph_text)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(forge_conv)
```

Don't forget to add at the top:
```python
from datetime import datetime
```

---

## 📊 What You've Built

✅ Working Telegram bot
✅ Interactive menu system
✅ Glyph storage (in-memory)
✅ Statistics tracking
✅ Dockerized deployment
✅ Conversation-based glyph creation

---

## 🚀 Next Steps

Now that you have the foundation, add features from the research doc:

### Easy Wins (Add This Week)
1. **SQLite Storage** - Replace `USER_GLYPHS` dict with database
2. **Glyph Editing** - Let users edit existing glyphs
3. **Categories/Tags** - Organize glyphs
4. **Export/Import** - Backup functionality

### Medium (Add This Month)
5. **Glyph Mixing** - Combine two glyphs
6. **Search** - Find glyphs by keywords
7. **Public Gallery** - Share glyphs with community
8. **Usage Charts** - Visualize statistics

### Advanced (Add Later)
9. **AI Optimization** - Use GPT to improve glyphs
10. **Marketplace** - Buy/sell premium glyphs
11. **Team Workspaces** - Collaborate on glyphs
12. **Voice Input** - Speak glyphs into existence

---

## 🐛 Troubleshooting

### Bot doesn't respond
- Check your token in `.env`
- Make sure bot is running: `docker-compose ps`
- Check logs: `docker-compose logs`

### "Invalid token" error
- Verify token from @BotFather
- No extra spaces in `.env`

### Can't connect to Telegram
- Check your internet connection
- Verify firewall isn't blocking

### Docker issues
- Make sure Docker daemon is running
- Try: `docker-compose down && docker-compose up --build`

---

## 📚 Resources

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Feature Research Doc](./FEATURE_RESEARCH.md)
- [Implementation Examples](./IMPLEMENTATION_EXAMPLES.md)

---

## 🎉 Success!

You now have a working Telegram bot that can:
- Accept commands
- Show interactive menus
- Store data
- Track statistics
- Run in Docker

**Time to add your unique features and make it yours!** 🚀

---

*Built with ❤️ for the Glyph-It Forge community*
