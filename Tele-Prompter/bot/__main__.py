#!/usr/bin/env python3
"""
Glyph-It Forge Telegram Bot
Minimal MVP version for quick deployment
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
GLYPH_NAME, GLYPH_TEXT = range(2)

# Simple in-memory storage (replace with database in production)
USER_GLYPHS = {}


def count_tokens(text: str) -> int:
    """Simple token counter (words * 0.75)"""
    return int(len(text.split()) * 0.75)


# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with main menu"""
    keyboard = [
        [InlineKeyboardButton("🔨 Forge Glyph", callback_data='forge')],
        [InlineKeyboardButton("📚 My Glyphs", callback_data='list')],
        [InlineKeyboardButton("📊 Statistics", callback_data='stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌟 **Welcome to Glyph-It Forge!**\n\n"
        "Create powerful prompts under 27 tokens.\n\n"
        "What would you like to do?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = (
        "📚 **Glyph-It Forge Help**\n\n"
        "**Commands:**\n"
        "/start - Open main menu\n"
        "/forge - Create a new glyph\n"
        "/list - View your glyphs\n"
        "/stats - See your statistics\n"
        "/help - Show this help\n\n"
        "**What's a Glyph?**\n"
        "A glyph is a powerful, compact prompt (under 27 tokens) "
        "that you can reuse in AI conversations.\n\n"
        "**Tips:**\n"
        "• Keep glyphs focused and clear\n"
        "• Use descriptive names\n"
        "• Aim for exactly 27 tokens for bonus points!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    user_id = update.effective_user.id
    glyphs = USER_GLYPHS.get(user_id, {})
    
    status_text = (
        f"✅ **Bot Status: Online**\n\n"
        f"👤 Your ID: `{user_id}`\n"
        f"📚 Your Glyphs: {len(glyphs)}\n"
        f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    await update.message.reply_text(status_text, parse_mode='Markdown')


# ============================================
# CALLBACK HANDLERS
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'forge':
        await show_forge_menu(query, context)
    elif query.data == 'list':
        await show_glyph_list(query, context)
    elif query.data == 'stats':
        await show_stats(query, context)
    elif query.data == 'help':
        await show_help(query, context)
    elif query.data == 'main_menu':
        await show_main_menu(query, context)
    elif query.data.startswith('use_'):
        await use_glyph(query, context)


async def show_main_menu(query, context):
    """Return to main menu"""
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


async def show_forge_menu(query, context):
    """Show forge options"""
    keyboard = [
        [InlineKeyboardButton("✍️ Create Custom", callback_data='forge_custom')],
        [InlineKeyboardButton("🎲 Use Template", callback_data='forge_template')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔨 **Forge a New Glyph**\n\n"
        "Choose creation method:\n\n"
        "• **Custom** - Type your own glyph\n"
        "• **Template** - Start from preset",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def show_glyph_list(query, context):
    """List user's glyphs"""
    user_id = query.from_user.id
    glyphs = USER_GLYPHS.get(user_id, {})
    
    if not glyphs:
        keyboard = [[InlineKeyboardButton("🔨 Create First Glyph", callback_data='forge')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📚 Your library is empty!\n\nCreate your first glyph to get started.",
            reply_markup=reply_markup
        )
        return
    
    text = "📚 **Your Glyph Library:**\n\n"
    keyboard = []
    
    for name, data in list(glyphs.items())[:10]:
        preview = data['text'][:35] + "..." if len(data['text']) > 35 else data['text']
        tokens = data['token_count']
        emoji = "🎯" if tokens == 27 else "📝"
        
        text += f"{emoji} **{name}** ({tokens} tokens)\n"
        text += f"   _{preview}_\n"
        text += f"   Uses: {data['uses']}\n\n"
        
        keyboard.append([InlineKeyboardButton(f"📋 {name}", callback_data=f'use_{name}')])
    
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
    perfect_27 = sum(1 for g in glyphs.values() if g['token_count'] == 27)
    
    text = f"📊 **Your Statistics**\n\n"
    text += f"📚 Total Glyphs: {total}\n"
    text += f"🔥 Total Uses: {total_uses}\n"
    text += f"📈 Average Uses: {avg_uses:.1f}\n"
    text += f"🎯 Perfect 27s: {perfect_27}\n\n"
    
    if glyphs:
        sorted_glyphs = sorted(glyphs.items(), key=lambda x: x[1]['uses'], reverse=True)[:3]
        text += "🏆 **Top 3 Most Used:**\n"
        for i, (name, data) in enumerate(sorted_glyphs, 1):
            text += f"{i}. {name} - {data['uses']} uses\n"
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_help(query, context):
    """Show help"""
    text = (
        "❓ **Glyph-It Forge Help**\n\n"
        "**What's a Glyph?**\n"
        "A glyph is a powerful, compact prompt (under 27 tokens) "
        "that you can reuse in AI conversations.\n\n"
        "**Commands:**\n"
        "/start - Open main menu\n"
        "/forge - Create a new glyph\n"
        "/list - View your glyphs\n"
        "/stats - See your statistics\n\n"
        "**Tips:**\n"
        "• Keep glyphs focused and clear\n"
        "• Use descriptive names\n"
        "• Aim for exactly 27 tokens!\n"
        "• Mix glyphs to create new ones\n"
    )
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def use_glyph(query, context):
    """Display glyph for use"""
    glyph_name = query.data.replace('use_', '')
    user_id = query.from_user.id
    
    glyphs = USER_GLYPHS.get(user_id, {})
    glyph_data = glyphs.get(glyph_name)
    
    if not glyph_data:
        await query.answer("Glyph not found!", show_alert=True)
        return
    
    # Increment usage counter
    glyph_data['uses'] += 1
    
    tokens = glyph_data['token_count']
    emoji = "🎯" if tokens == 27 else "📝"
    
    text = (
        f"{emoji} **Using Glyph: {glyph_name}**\n\n"
        f"```\n{glyph_data['text']}\n```\n\n"
        f"📊 Tokens: {tokens}/27\n"
        f"🔥 Total uses: {glyph_data['uses']}\n\n"
        f"_Copy the text above to use in your AI chat!_"
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 Back to List", callback_data='list')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ============================================
# CONVERSATION HANDLERS (Glyph Creation)
# ============================================

async def forge_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start glyph creation"""
    await update.message.reply_text(
        "🔨 **Let's forge a glyph!**\n\n"
        "Step 1/2: Give it a name (one word, no spaces):\n\n"
        "_Example: code_helper, creative_muse, debug_wizard_",
        parse_mode='Markdown'
    )
    return GLYPH_NAME


async def get_glyph_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get glyph name"""
    name = update.message.text.strip().replace(' ', '_').lower()
    
    # Validate name
    if len(name) > 30:
        await update.message.reply_text(
            "⚠️ Name too long! Keep it under 30 characters.\n"
            "Try again:"
        )
        return GLYPH_NAME
    
    if not name.replace('_', '').isalnum():
        await update.message.reply_text(
            "⚠️ Use only letters, numbers, and underscores.\n"
            "Try again:"
        )
        return GLYPH_NAME
    
    # Check if name already exists
    user_id = update.effective_user.id
    if user_id in USER_GLYPHS and name in USER_GLYPHS[user_id]:
        await update.message.reply_text(
            f"⚠️ You already have a glyph named '{name}'.\n"
            "Choose a different name:"
        )
        return GLYPH_NAME
    
    context.user_data['glyph_name'] = name
    
    await update.message.reply_text(
        f"✅ Name: **{name}**\n\n"
        f"Step 2/2: Enter your glyph text.\n\n"
        f"🎯 **Goal:** Keep it under 27 tokens!\n"
        f"📝 **Tip:** ~20-25 words = ~27 tokens\n\n"
        f"Type your glyph:",
        parse_mode='Markdown'
    )
    return GLYPH_TEXT


async def get_glyph_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get glyph text and save"""
    text = update.message.text.strip()
    name = context.user_data['glyph_name']
    user_id = update.effective_user.id
    
    # Count tokens
    token_count = count_tokens(text)
    
    # Warning if too long
    if token_count > 27:
        await update.message.reply_text(
            f"⚠️ **Too long!** ({token_count} tokens)\n\n"
            f"Your glyph needs to be under 27 tokens.\n"
            f"Current: {token_count} tokens\n"
            f"Need to cut: {token_count - 27} tokens\n\n"
            f"Please shorten it and try again:"
        )
        return GLYPH_TEXT
    
    # Save glyph
    if user_id not in USER_GLYPHS:
        USER_GLYPHS[user_id] = {}
    
    USER_GLYPHS[user_id][name] = {
        'text': text,
        'token_count': token_count,
        'uses': 0,
        'created': datetime.now().isoformat()
    }
    
    # Success message
    emoji = "🎯" if token_count == 27 else "✨"
    perfect_msg = "\n\n🎉 **PERFECT!** Exactly 27 tokens!" if token_count == 27 else ""
    
    await update.message.reply_text(
        f"{emoji} **Glyph forged successfully!**{perfect_msg}\n\n"
        f"**Name:** {name}\n"
        f"**Tokens:** {token_count}/27\n\n"
        f"```\n{text}\n```\n\n"
        f"Use /list to see all your glyphs!",
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "❌ Cancelled.\n\nUse /start to return to the main menu."
    )
    return ConversationHandler.END


# ============================================
# MAIN
# ============================================

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment!")
        logger.error("Set it in your .env file or environment variables.")
        return
    
    logger.info("🚀 Starting Glyph-It Forge Bot...")
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('status', status))
    
    # Conversation handler for glyph creation
    forge_conv = ConversationHandler(
        entry_points=[CommandHandler('forge', forge_start)],
        states={
            GLYPH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_glyph_name)],
            GLYPH_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_glyph_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(forge_conv)
    
    # Callback query handlers
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    logger.info("✅ Bot is ready! Send /start to begin.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
