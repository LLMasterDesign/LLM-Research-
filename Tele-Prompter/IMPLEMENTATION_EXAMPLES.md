# Telegram Prompt Features - Implementation Examples

Quick-start code snippets for implementing the most popular features from the research.

---

## 🔧 Setup: Basic Bot Structure

```python
# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize your glyph storage (simple dict for MVP)
GLYPHS = {}
USER_USAGE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with main menu"""
    keyboard = [
        [InlineKeyboardButton("🔨 Forge New Glyph", callback_data='forge')],
        [InlineKeyboardButton("📚 My Glyphs", callback_data='list')],
        [InlineKeyboardButton("⭐ Marketplace", callback_data='market')],
        [InlineKeyboardButton("📊 My Stats", callback_data='stats')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌟 Welcome to Glyph-It Forge!\n\n"
        "Create, manage, and use powerful prompts.\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )

def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    app.add_handler(CommandHandler("start", start))
    
    app.run_polling()

if __name__ == '__main__':
    main()
```

---

## 🎯 Feature 1: Interactive Glyph Forge

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler

# States for conversation
CHOOSE_SEED, CHOOSE_INTENSITY, CHOOSE_STYLE, PREVIEW = range(4)

async def forge_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the forge process"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🧠 Wisdom", callback_data='seed_wisdom')],
        [InlineKeyboardButton("⚡ Power", callback_data='seed_power')],
        [InlineKeyboardButton("⚖️ Balance", callback_data='seed_balance')],
        [InlineKeyboardButton("🌀 Chaos", callback_data='seed_chaos')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔨 **Glyph Forge Activated**\n\n"
        "Step 1/3: Choose your seed essence 🌱",
        reply_markup=reply_markup
    )
    return CHOOSE_SEED

async def choose_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle seed selection"""
    query = update.callback_query
    await query.answer()
    
    seed = query.data.replace('seed_', '')
    context.user_data['glyph_seed'] = seed
    
    keyboard = [
        [InlineKeyboardButton("💨 Subtle", callback_data='intensity_subtle')],
        [InlineKeyboardButton("🔥 Medium", callback_data='intensity_medium')],
        [InlineKeyboardButton("⚡ Intense", callback_data='intensity_intense')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Seed: **{seed.title()}**\n\n"
        "Step 2/3: Choose intensity ⚡",
        reply_markup=reply_markup
    )
    return CHOOSE_INTENSITY

async def choose_intensity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle intensity selection"""
    query = update.callback_query
    await query.answer()
    
    intensity = query.data.replace('intensity_', '')
    context.user_data['glyph_intensity'] = intensity
    
    keyboard = [
        [InlineKeyboardButton("📝 Poetic", callback_data='style_poetic')],
        [InlineKeyboardButton("🔧 Technical", callback_data='style_technical')],
        [InlineKeyboardButton("🔮 Mystical", callback_data='style_mystical')],
        [InlineKeyboardButton("💼 Professional", callback_data='style_professional')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Seed: **{context.user_data['glyph_seed'].title()}**\n"
        f"✅ Intensity: **{intensity.title()}**\n\n"
        "Step 3/3: Choose style 🎨",
        reply_markup=reply_markup
    )
    return CHOOSE_STYLE

async def preview_glyph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate and preview the glyph"""
    query = update.callback_query
    await query.answer()
    
    style = query.data.replace('style_', '')
    context.user_data['glyph_style'] = style
    
    # Generate glyph based on choices
    glyph = generate_glyph(
        context.user_data['glyph_seed'],
        context.user_data['glyph_intensity'],
        style
    )
    
    context.user_data['generated_glyph'] = glyph
    
    keyboard = [
        [InlineKeyboardButton("✅ Save Glyph", callback_data='save_glyph')],
        [InlineKeyboardButton("🔄 Regenerate", callback_data='forge')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎨 **Your Forged Glyph:**\n\n"
        f"```\n{glyph}\n```\n\n"
        f"Seed: {context.user_data['glyph_seed']} | "
        f"Intensity: {context.user_data['glyph_intensity']} | "
        f"Style: {style}\n\n"
        f"Token count: {len(glyph.split())} tokens",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PREVIEW

def generate_glyph(seed, intensity, style):
    """Generate glyph based on parameters"""
    templates = {
        'wisdom': {
            'poetic': "You are a sage who speaks in {intensity} metaphors about {topic}",
            'technical': "Analyze {topic} with {intensity} depth and scholarly precision",
            'mystical': "Channel ancient wisdom to illuminate {topic} with {intensity} insight",
            'professional': "Provide {intensity} expert analysis on {topic}"
        },
        'power': {
            'poetic': "Unleash {intensity} creative force to transform {topic}",
            'technical': "Execute {intensity} optimization strategies for {topic}",
            'mystical': "Summon {intensity} transformative energy around {topic}",
            'professional': "Drive {intensity} results in {topic} implementation"
        },
        # Add more combinations...
    }
    
    template = templates.get(seed, {}).get(style, "You are a helpful assistant for {topic}")
    
    # Apply intensity modifiers
    intensity_map = {
        'subtle': 'gentle',
        'medium': 'balanced',
        'intense': 'maximum'
    }
    
    return template.format(
        intensity=intensity_map.get(intensity, 'moderate'),
        topic='{topic}'  # Keep as placeholder for later use
    )

# Setup the conversation handler
forge_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(forge_start, pattern='^forge$')],
    states={
        CHOOSE_SEED: [CallbackQueryHandler(choose_seed, pattern='^seed_')],
        CHOOSE_INTENSITY: [CallbackQueryHandler(choose_intensity, pattern='^intensity_')],
        CHOOSE_STYLE: [CallbackQueryHandler(preview_glyph, pattern='^style_')],
        PREVIEW: [
            CallbackQueryHandler(save_glyph, pattern='^save_glyph$'),
            CallbackQueryHandler(forge_start, pattern='^forge$'),
        ],
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
)
```

---

## 📚 Feature 2: Glyph Library with Pagination

```python
import json
from math import ceil

class GlyphStorage:
    def __init__(self, file_path='data/glyphs.json'):
        self.file_path = file_path
        self.load()
    
    def load(self):
        try:
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {'glyphs': {}, 'user_glyphs': {}}
    
    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_glyph(self, user_id, glyph_name, glyph_text, metadata=None):
        if str(user_id) not in self.data['user_glyphs']:
            self.data['user_glyphs'][str(user_id)] = {}
        
        self.data['user_glyphs'][str(user_id)][glyph_name] = {
            'text': glyph_text,
            'created': str(datetime.now()),
            'usage_count': 0,
            'metadata': metadata or {}
        }
        self.save()
    
    def get_user_glyphs(self, user_id):
        return self.data['user_glyphs'].get(str(user_id), {})
    
    def increment_usage(self, user_id, glyph_name):
        try:
            self.data['user_glyphs'][str(user_id)][glyph_name]['usage_count'] += 1
            self.save()
        except KeyError:
            pass

storage = GlyphStorage()

async def list_glyphs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user's glyphs with pagination"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    glyphs = storage.get_user_glyphs(user_id)
    
    if not glyphs:
        await query.edit_message_text(
            "📚 Your glyph library is empty!\n\n"
            "Use /forge to create your first glyph."
        )
        return
    
    # Pagination
    page = context.user_data.get('glyph_page', 0)
    items_per_page = 5
    glyph_list = list(glyphs.items())
    total_pages = ceil(len(glyph_list) / items_per_page)
    
    start = page * items_per_page
    end = start + items_per_page
    current_glyphs = glyph_list[start:end]
    
    # Build message
    text = f"📚 **Your Glyphs** (Page {page + 1}/{total_pages})\n\n"
    
    keyboard = []
    for name, data in current_glyphs:
        usage = data['usage_count']
        preview = data['text'][:40] + "..." if len(data['text']) > 40 else data['text']
        text += f"🔹 **{name}**\n   {preview}\n   Uses: {usage}\n\n"
        keyboard.append([InlineKeyboardButton(f"Use: {name}", callback_data=f'use_{name}')])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data='glyphs_prev'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data='glyphs_next'))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def use_glyph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Use a glyph"""
    query = update.callback_query
    await query.answer()
    
    glyph_name = query.data.replace('use_', '')
    user_id = update.effective_user.id
    
    glyphs = storage.get_user_glyphs(user_id)
    glyph_data = glyphs.get(glyph_name)
    
    if not glyph_data:
        await query.answer("Glyph not found!", show_alert=True)
        return
    
    # Increment usage counter
    storage.increment_usage(user_id, glyph_name)
    
    await query.edit_message_text(
        f"✨ **Using Glyph: {glyph_name}**\n\n"
        f"```\n{glyph_data['text']}\n```\n\n"
        f"Total uses: {glyph_data['usage_count'] + 1}\n\n"
        "_Copy the text above to use in your AI chat!_",
        parse_mode='Markdown'
    )
```

---

## 📊 Feature 3: Usage Analytics

```python
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    glyphs = storage.get_user_glyphs(user_id)
    
    if not glyphs:
        await query.edit_message_text("No glyphs yet! Create one with /forge")
        return
    
    # Calculate stats
    total_glyphs = len(glyphs)
    total_uses = sum(g['usage_count'] for g in glyphs.values())
    
    # Most used
    sorted_glyphs = sorted(
        glyphs.items(), 
        key=lambda x: x[1]['usage_count'], 
        reverse=True
    )
    top_3 = sorted_glyphs[:3]
    
    # Build message
    text = f"📊 **Your Glyph Statistics**\n\n"
    text += f"📚 Total Glyphs: {total_glyphs}\n"
    text += f"🔥 Total Uses: {total_uses}\n"
    text += f"📈 Average Uses: {total_uses / total_glyphs:.1f}\n\n"
    
    text += "🏆 **Top 3 Most Used:**\n"
    for i, (name, data) in enumerate(top_3, 1):
        text += f"{i}. {name} - {data['usage_count']} uses\n"
    
    # Generate chart
    chart_file = generate_usage_chart(glyphs)
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if chart_file:
        await query.message.reply_photo(
            photo=chart_file,
            caption=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await query.delete_message()
    else:
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

def generate_usage_chart(glyphs):
    """Generate bar chart of glyph usage"""
    if not glyphs:
        return None
    
    # Get top 10
    sorted_glyphs = sorted(
        glyphs.items(),
        key=lambda x: x[1]['usage_count'],
        reverse=True
    )[:10]
    
    names = [name[:15] + "..." if len(name) > 15 else name for name, _ in sorted_glyphs]
    uses = [data['usage_count'] for _, data in sorted_glyphs]
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.bar(names, uses, color='#5865F2')
    plt.xlabel('Glyph Name')
    plt.ylabel('Usage Count')
    plt.title('Top 10 Most Used Glyphs')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save to BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()
    
    return buf
```

---

## 🔄 Feature 4: Glyph Mixing (Facet Forge)

```python
async def mix_glyphs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mix two glyphs to create a new one"""
    # Usage: /mix glyph1 glyph2
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /mix <glyph1> <glyph2>\n\n"
            "Combines two glyphs into a new hybrid!"
        )
        return
    
    user_id = update.effective_user.id
    glyphs = storage.get_user_glyphs(user_id)
    
    glyph1_name = context.args[0]
    glyph2_name = context.args[1]
    
    glyph1 = glyphs.get(glyph1_name)
    glyph2 = glyphs.get(glyph2_name)
    
    if not glyph1 or not glyph2:
        await update.message.reply_text("One or both glyphs not found!")
        return
    
    # Simple mixing: combine key elements
    mixed_glyph = create_hybrid(glyph1['text'], glyph2['text'])
    
    keyboard = [
        [InlineKeyboardButton("✅ Save", callback_data='save_mixed')],
        [InlineKeyboardButton("🔄 Remix", callback_data='remix')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['mixed_glyph'] = mixed_glyph
    context.user_data['parent_glyphs'] = [glyph1_name, glyph2_name]
    
    await update.message.reply_text(
        f"🧪 **Mixed Glyph Created!**\n\n"
        f"Parents: {glyph1_name} + {glyph2_name}\n\n"
        f"```\n{mixed_glyph}\n```\n\n"
        f"Token count: {len(mixed_glyph.split())}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def create_hybrid(glyph1, glyph2):
    """Create hybrid prompt from two glyphs"""
    # Simple approach: extract key phrases and combine
    # In production, use LLM for sophisticated mixing
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    
    words1 = [w for w in glyph1.lower().split() if w not in stop_words]
    words2 = [w for w in glyph2.lower().split() if w not in stop_words]
    
    # Extract unique words from each
    unique1 = set(words1) - set(words2)
    unique2 = set(words2) - set(words1)
    common = set(words1) & set(words2)
    
    # Build hybrid (this is simplified - use LLM for better results)
    hybrid_parts = []
    
    if unique1:
        hybrid_parts.append(' '.join(list(unique1)[:3]))
    if common:
        hybrid_parts.append(' '.join(list(common)[:2]))
    if unique2:
        hybrid_parts.append(' '.join(list(unique2)[:3]))
    
    hybrid = f"You are a hybrid assistant combining {' and '.join(hybrid_parts)}"
    
    return hybrid

# For production, use LLM mixing:
async def create_hybrid_with_ai(glyph1, glyph2):
    """Use LLM to create sophisticated hybrid"""
    import openai
    
    prompt = f"""Create a new prompt by intelligently combining these two prompts.
Keep it under 27 tokens. Maintain the best aspects of both.

Prompt 1: {glyph1}
Prompt 2: {glyph2}

New combined prompt:"""
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60
    )
    
    return response.choices[0].message.content.strip()
```

---

## 🛒 Feature 5: Simple Marketplace

```python
class Marketplace:
    def __init__(self):
        self.featured_glyphs = {
            'code_wizard': {
                'text': 'You are an expert programmer who explains code with clarity and wisdom',
                'price': 100,  # Credits
                'author': 'system',
                'category': 'programming',
                'rating': 4.8,
                'downloads': 1523
            },
            'creative_muse': {
                'text': 'Channel creative inspiration to generate unique artistic ideas',
                'price': 75,
                'author': 'system',
                'category': 'creative',
                'rating': 4.9,
                'downloads': 2103
            },
            # Add more...
        }
    
    def get_featured(self, category=None):
        if category:
            return {k: v for k, v in self.featured_glyphs.items() 
                   if v['category'] == category}
        return self.featured_glyphs

marketplace = Marketplace()

async def show_marketplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display marketplace"""
    query = update.callback_query
    await query.answer()
    
    featured = marketplace.get_featured()
    
    text = "⭐ **Glyph Marketplace**\n\n"
    text += "Discover and unlock premium glyphs!\n\n"
    
    keyboard = []
    for glyph_id, data in list(featured.items())[:5]:
        stars = "⭐" * int(data['rating'])
        button_text = f"{glyph_id} - {data['price']} 💎 {stars}"
        keyboard.append([InlineKeyboardButton(
            button_text, 
            callback_data=f'market_view_{glyph_id}'
        )])
    
    keyboard.append([InlineKeyboardButton("💰 My Balance", callback_data='balance')])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def view_marketplace_glyph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View individual marketplace glyph"""
    query = update.callback_query
    await query.answer()
    
    glyph_id = query.data.replace('market_view_', '')
    glyph_data = marketplace.featured_glyphs.get(glyph_id)
    
    if not glyph_data:
        await query.answer("Glyph not found!", show_alert=True)
        return
    
    text = f"📦 **{glyph_id}**\n\n"
    text += f"```\n{glyph_data['text']}\n```\n\n"
    text += f"💎 Price: {glyph_data['price']} credits\n"
    text += f"⭐ Rating: {glyph_data['rating']}/5\n"
    text += f"📥 Downloads: {glyph_data['downloads']}\n"
    text += f"📁 Category: {glyph_data['category']}\n"
    
    keyboard = [
        [InlineKeyboardButton("🛒 Purchase", callback_data=f'buy_{glyph_id}')],
        [InlineKeyboardButton("🔙 Back to Market", callback_data='market')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
```

---

## 🗄️ Feature 6: SQLite Database Setup

```python
import sqlite3
from datetime import datetime

class GlyphDatabase:
    def __init__(self, db_path='data/glyphs.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Glyphs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS glyphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                category TEXT,
                is_public BOOLEAN DEFAULT 0,
                UNIQUE(user_id, name)
            )
        ''')
        
        # Usage log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                glyph_id INTEGER,
                user_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (glyph_id) REFERENCES glyphs(id)
            )
        ''')
        
        # User credits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_credits (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                earned INTEGER DEFAULT 0,
                spent INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_glyph(self, user_id, name, text, category=None):
        """Add a new glyph"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO glyphs (user_id, name, text, category)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, text, category))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate name
        finally:
            conn.close()
    
    def get_user_glyphs(self, user_id):
        """Get all glyphs for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, text, created_at, usage_count, category
            FROM glyphs
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        glyphs = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': g[0],
                'name': g[1],
                'text': g[2],
                'created_at': g[3],
                'usage_count': g[4],
                'category': g[5]
            }
            for g in glyphs
        ]
    
    def log_usage(self, glyph_id, user_id):
        """Log glyph usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert log entry
        cursor.execute('''
            INSERT INTO usage_log (glyph_id, user_id)
            VALUES (?, ?)
        ''', (glyph_id, user_id))
        
        # Increment usage count
        cursor.execute('''
            UPDATE glyphs
            SET usage_count = usage_count + 1
            WHERE id = ?
        ''', (glyph_id,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, user_id):
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total glyphs
        cursor.execute('SELECT COUNT(*) FROM glyphs WHERE user_id = ?', (user_id,))
        total_glyphs = cursor.fetchone()[0]
        
        # Total uses
        cursor.execute('''
            SELECT SUM(usage_count) FROM glyphs WHERE user_id = ?
        ''', (user_id,))
        total_uses = cursor.fetchone()[0] or 0
        
        # Most used
        cursor.execute('''
            SELECT name, usage_count
            FROM glyphs
            WHERE user_id = ?
            ORDER BY usage_count DESC
            LIMIT 5
        ''', (user_id,))
        top_glyphs = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_glyphs': total_glyphs,
            'total_uses': total_uses,
            'top_glyphs': top_glyphs
        }

# Usage
db = GlyphDatabase()
```

---

## 🐳 Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Run the bot
CMD ["python", "-m", "bot"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  bot:
    build: .
    container_name: glyph_forge_bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_URL=postgresql://postgres:password@db:5432/glyphforge
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/app/data
    depends_on:
      - db
      - redis
    networks:
      - glyph_network

  db:
    image: postgres:15-alpine
    container_name: glyph_db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=glyphforge
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - glyph_network

  redis:
    image: redis:7-alpine
    container_name: glyph_redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - glyph_network

volumes:
  postgres_data:
  redis_data:

networks:
  glyph_network:
    driver: bridge
```

```bash
# .env.example
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=optional_for_ai_features
DATABASE_URL=sqlite:///data/glyphs.db
REDIS_URL=redis://localhost:6379/0
```

---

## 🚀 Quick Start Commands

```bash
# 1. Clone/setup project
mkdir glyph-forge-bot
cd glyph-forge-bot

# 2. Create requirements.txt
cat > requirements.txt << EOF
python-telegram-bot==20.7
python-dotenv==1.0.0
sqlalchemy==2.0.23
matplotlib==3.8.2
redis==5.0.1
EOF

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# 5. Run bot
python bot.py

# Or with Docker:
docker-compose up -d
```

---

## 🔑 Key Takeaways

1. **Start Simple**: Basic storage (JSON/SQLite) works fine for MVP
2. **Incremental Features**: Add one feature at a time, test thoroughly
3. **User State**: Use `context.user_data` for conversation flows
4. **Callbacks**: InlineKeyboard + CallbackQueryHandler for rich interactions
5. **Persistence**: SQLite → PostgreSQL as you scale
6. **Docker**: Makes deployment consistent and easy

---

**Next**: Pick 3-5 features from the research doc and implement them using these patterns!
