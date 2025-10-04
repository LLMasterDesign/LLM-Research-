# Telegram Bot Features - Quick Reference Cheat Sheet

**One-page reference for building Telegram prompt bots**

---

## 🎯 Top 20 Features (Priority Ranked)

| # | Feature | Effort | Impact | Code Complexity |
|---|---------|--------|--------|-----------------|
| 1 | Basic CRUD (Create/Read/Update/Delete) | Low | High | ⭐ |
| 2 | Token Counter with Progress Bar | Low | High | ⭐ |
| 3 | Usage Tracking & Stats | Low | Medium | ⭐ |
| 4 | Interactive Forge Builder | Medium | High | ⭐⭐ |
| 5 | Search & Filter | Low | Medium | ⭐ |
| 6 | Public Gallery/Share | Medium | High | ⭐⭐ |
| 7 | Glyph Mixing | Medium | High | ⭐⭐ |
| 8 | Achievement System | Low | Medium | ⭐ |
| 9 | AI Compression to 27 Tokens | Medium | High | ⭐⭐⭐ |
| 10 | Inline Query Search | Low | Medium | ⭐ |
| 11 | Categories/Tags | Low | Medium | ⭐ |
| 12 | Export/Import (JSON) | Low | Medium | ⭐ |
| 13 | Daily Challenges | Medium | Medium | ⭐⭐ |
| 14 | Token Economy/Credits | Medium | Medium | ⭐⭐ |
| 15 | Marketplace | High | High | ⭐⭐⭐ |
| 16 | Semantic Search (Embeddings) | High | Medium | ⭐⭐⭐ |
| 17 | Team Workspaces | High | Medium | ⭐⭐⭐ |
| 18 | Voice-to-Glyph | Medium | Low | ⭐⭐ |
| 19 | WebApp Integration | High | High | ⭐⭐⭐ |
| 20 | API Access | Medium | Low | ⭐⭐ |

---

## 🚀 MVP Feature Set (Build These First)

```
Week 1-2: Core Functionality
✅ Bot setup with commands (/start, /help)
✅ Create glyph (conversational flow)
✅ List glyphs (with pagination)
✅ View/delete glyph
✅ Token counter (27-token limit)
✅ SQLite storage
✅ Docker deployment

Result: Working bot users can test
```

---

## 📋 Essential Commands

```python
/start        # Welcome + main menu
/forge        # Create new glyph
/list         # Show all glyphs
/use <name>   # Display glyph for copying
/stats        # Show statistics
/search <q>   # Search glyphs
/mix <g1> <g2># Combine glyphs
/delete <name># Remove glyph
/help         # Show help
```

---

## 🎨 Key Code Patterns

### 1. Basic Command Handler
```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome!")
```

### 2. Inline Keyboard Menu
```python
keyboard = [
    [InlineKeyboardButton("Option 1", callback_data='opt1')],
    [InlineKeyboardButton("Option 2", callback_data='opt2')],
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Choose:", reply_markup=reply_markup)
```

### 3. Callback Handler
```python
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'opt1':
        await query.edit_message_text("You chose Option 1")
```

### 4. Conversation Flow
```python
STEP1, STEP2 = range(2)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_conversation)],
    states={
        STEP1: [MessageHandler(filters.TEXT, handle_step1)],
        STEP2: [MessageHandler(filters.TEXT, handle_step2)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
```

### 5. Token Counter
```python
def count_tokens(text: str) -> int:
    return len(text.split())  # Simple estimate
    
# Or accurate with tiktoken:
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4")
return len(encoding.encode(text))
```

---

## 🗄️ Database Schema (SQLite)

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    credits INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Glyphs table
CREATE TABLE glyphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    category TEXT,
    is_public BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id),
    UNIQUE(user_id, name)
);

-- Usage log
CREATE TABLE usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    glyph_id INTEGER,
    user_id INTEGER,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (glyph_id) REFERENCES glyphs(id)
);

-- Achievements
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    achievement_type TEXT,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
);
```

---

## 🐳 Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "bot"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  bot:
    build: .
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    env_file:
      - .env
```

### .env
```bash
TELEGRAM_BOT_TOKEN=your_token_here
DATABASE_URL=sqlite:///data/glyphs.db
OPENAI_API_KEY=optional
```

---

## 📊 Key Metrics to Track

```python
# User Metrics
- Total registered users
- Daily/Weekly/Monthly active users (DAU/WAU/MAU)
- Retention rate (7-day, 30-day)
- Churn rate

# Glyph Metrics
- Total glyphs created
- Average glyphs per user
- Most used glyphs (global)
- Perfect 27-token glyphs count

# Engagement Metrics
- Average session length
- Commands per session
- Feature usage breakdown
- Search query rate

# Business Metrics (if monetized)
- Conversion rate (free → paid)
- Monthly Recurring Revenue (MRR)
- Customer Lifetime Value (LTV)
- Churn rate
```

---

## 🎯 27-Token Specific Features

```python
# Real-time token display
def show_token_progress(tokens: int) -> str:
    progress = min(tokens / 27, 1.0)
    filled = int(progress * 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    if tokens > 27:
        emoji = "🔴"
    elif tokens == 27:
        emoji = "🎯"
    else:
        emoji = "🟢"
    
    return f"{emoji} [{bar}] {tokens}/27 tokens"

# Achievement for perfect 27
if token_count == 27:
    unlock_achievement(user_id, 'perfect_27')
    
# Token efficiency score
def efficiency_score(text: str, uses: int) -> float:
    tokens = count_tokens(text)
    token_efficiency = 1.0 - abs(27 - tokens) / 27
    return (uses / 100) * token_efficiency * 100

# The 27 Club (exclusive)
def is_in_27_club(user_id: int) -> bool:
    glyphs = get_user_glyphs(user_id)
    return any(count_tokens(g['text']) == 27 for g in glyphs.values())
```

---

## 🎮 Gamification Elements

```python
ACHIEVEMENTS = {
    'first_glyph': {'name': '🌱 Seed Planted', 'points': 10},
    'perfect_27': {'name': '🎯 Perfect Shot', 'points': 50},
    'ten_glyphs': {'name': '📚 Librarian', 'points': 30},
    'hundred_uses': {'name': '🔥 Power User', 'points': 100},
    'mixer': {'name': '🧪 Alchemist', 'points': 40},
    'sharer': {'name': '🤝 Community Champion', 'points': 60},
}

LEVELS = [
    (0, 'Novice'),
    (100, 'Apprentice'),
    (250, 'Journeyman'),
    (500, 'Expert'),
    (1000, 'Master'),
    (2500, 'Grandmaster'),
]
```

---

## 🔧 Common Code Snippets

### Pagination
```python
def paginate(items: list, page: int, per_page: int = 5):
    start = page * per_page
    end = start + per_page
    return items[start:end], len(items) // per_page + 1
```

### User State Management
```python
# Store in context
context.user_data['current_glyph'] = glyph_name
context.user_data['forge_step'] = 2

# Retrieve
current = context.user_data.get('current_glyph')
```

### Error Handling
```python
try:
    # Your code
    pass
except Exception as e:
    logger.error(f"Error: {e}")
    await update.message.reply_text(
        "⚠️ Something went wrong. Please try again."
    )
```

### Rate Limiting
```python
from functools import wraps
import time

user_last_request = {}

def rate_limit(seconds: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            user_id = update.effective_user.id
            now = time.time()
            
            if user_id in user_last_request:
                if now - user_last_request[user_id] < seconds:
                    await update.message.reply_text("⏱️ Slow down! Wait a bit.")
                    return
            
            user_last_request[user_id] = now
            return await func(update, context)
        return wrapper
    return decorator
```

---

## 🚨 Common Pitfalls to Avoid

1. **No error handling** → Bot crashes on invalid input
2. **Blocking operations** → Use `async/await` properly
3. **No rate limiting** → Users abuse features
4. **Storing tokens in code** → Use environment variables
5. **No logging** → Can't debug production issues
6. **Large message edits** → Telegram has size limits
7. **Ignoring user_data cleanup** → Memory leaks
8. **No input validation** → SQL injection, XSS risks
9. **Hardcoded strings** → Use constants/config
10. **No backups** → Data loss when things break

---

## 📚 Essential Libraries

```txt
# Core
python-telegram-bot==20.7
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
aiosqlite==0.19.0      # For async SQLite
psycopg2-binary==2.9.9 # For PostgreSQL

# AI/LLM (optional)
openai==1.3.5
anthropic==0.7.0
tiktoken==0.5.1

# Analytics
matplotlib==3.8.2
pandas==2.1.3

# Utilities
httpx==0.25.2          # HTTP client
redis==5.0.1           # Caching
```

---

## 🎯 Launch Checklist

### Pre-Launch
- [ ] All core commands work
- [ ] Error handling implemented
- [ ] Database migrations tested
- [ ] Docker deployment works
- [ ] Backup system in place
- [ ] Rate limiting configured
- [ ] Logging set up
- [ ] Help command comprehensive

### Launch Day
- [ ] Monitor logs actively
- [ ] Be available for support
- [ ] Track key metrics
- [ ] Gather user feedback
- [ ] Note common issues

### Post-Launch
- [ ] Fix critical bugs within 24h
- [ ] Release patch within 48h
- [ ] Survey early users
- [ ] Iterate on feedback
- [ ] Plan next features

---

## 💰 Pricing Ideas

### Freemium
```
Free:
- 25 glyphs
- Basic features
- Public gallery access

Pro ($5/mo):
- Unlimited glyphs
- AI compression
- Advanced analytics
- Priority support

Team ($20/mo):
- Shared workspace
- Collaboration tools
- Team analytics
- Admin controls
```

### Credits
```
Starter Pack: $2 = 200 credits
Power Pack: $5 = 600 credits
Ultimate: $10 = 1500 credits

Usage:
- AI compress: 10 credits
- Marketplace glyph: 50-200 credits
- Featured placement: 100 credits
```

---

## 🔗 Quick Links

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SQLAlchemy docs](https://docs.sqlalchemy.org/)
- [Docker docs](https://docs.docker.com/)
- [OpenAI API](https://platform.openai.com/docs/)

---

## 🎉 Success Formula

```
MVP (2 weeks) + 
First Users (week 3) + 
Feedback Loop (ongoing) + 
Weekly Iterations = 
Success
```

**Key:** Ship fast, learn fast, improve fast! 🚀

---

*This cheat sheet covers 80% of what you need to build a successful Telegram prompt bot.*
