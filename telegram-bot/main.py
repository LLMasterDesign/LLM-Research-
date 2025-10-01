#!/usr/bin/env python3
"""
Τ{Raven} - Telegram Command Station
Main bot entry point
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram_bot.handlers.commands import (
    start_command,
    help_command,
    ask_command,
    context_command,
    git_command,
    file_command,
    run_command,
    session_command,
)
from telegram_bot.services.context_tracker import ContextTracker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/raven.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot."""
    allowed_users = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
    return str(user_id) in allowed_users or len(allowed_users) == 0


async def authorization_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[bool]:
    """Middleware to check user authorization."""
    if not update.effective_user:
        return False
    
    user_id = update.effective_user.id
    if not check_authorized(user_id):
        logger.warning(f"Unauthorized access attempt from user {user_id}")
        await update.message.reply_text(
            "🚫 Unauthorized. You don't have access to this bot.\n\n"
            "If you believe this is an error, please contact the administrator."
        )
        return False
    
    return True


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            f"⚠️ An error occurred:\n\n`{str(context.error)}`\n\n"
            "Please try again or contact support if the issue persists.",
            parse_mode='Markdown'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages (non-commands)."""
    if not await authorization_middleware(update, context):
        return
    
    # Treat regular messages as /ask commands
    message_text = update.message.text
    
    # Store message in context for /ask handler
    context.args = [message_text]
    await ask_command(update, context)


def main() -> None:
    """Start the bot."""
    # Validate required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and fill in your configuration.")
        sys.exit(1)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Initialize context tracker
    workspace_path = os.getenv('WORKSPACE_PATH', '/workspace')
    context_tracker = ContextTracker(workspace_path)
    
    logger.info("🚀 Starting Τ{Raven} - Telegram Command Station")
    logger.info(f"📂 Workspace: {workspace_path}")
    
    # Create application
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = Application.builder().token(token).build()
    
    # Store context tracker in bot data
    application.bot_data['context_tracker'] = context_tracker
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("context", context_command))
    application.add_handler(CommandHandler("git", git_command))
    application.add_handler(CommandHandler("file", file_command))
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("session", session_command))
    
    # Handle regular messages as /ask commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
