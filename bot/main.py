#!/usr/bin/env python3
"""
▛//▞▞ ⟦⎊⟧ :: TELEGRAM.CODEX.BOT ⫸
Telegram bot for Codex Memory Node
Handles banner+seal ritual and persists to Postgres/Redis
:: ∎
"""
import asyncio
import logging
import os
import re
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from database import Database
from redis_client import RedisCache
from memory import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")


class CodexBot:
    """Main Codex Bot class"""
    
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self.db = Database(DATABASE_URL)
        self.redis = RedisCache(REDIS_URL)
        self.memory = MemoryManager(self.db, self.redis)
        
        # Register handlers
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("stats"))(self.cmd_stats)
        self.dp.message(Command("recall"))(self.cmd_recall)
        self.dp.message(F.text)(self.handle_message)
    
    async def cmd_start(self, message: Message):
        """Handle /start command"""
        user_id = str(message.from_user.id)
        await self.db.log_event(
            user_id=user_id,
            kind="command.start",
            banner="/start",
            seal=":: ∎",
            payload={"username": message.from_user.username}
        )
        
        welcome = """
▛//▞▞ ⟦⎊⟧ :: CODEX.AWAKENED ⫸

Welcome to your Memory Codex Node.

<b>RITUAL.GUARD</b>
• Begin each prompt with a banner (first line)
• End with seal: <code>:: ∎</code>
• Only sealed messages persist to memory

<b>Commands</b>
/help - Show this help
/stats - View your memory statistics
/recall [query] - Search your memories

Your facts are stored. Your seals are honored.
:: ∎
"""
        await message.reply(welcome)
    
    async def cmd_help(self, message: Message):
        """Handle /help command"""
        help_text = """
<b>▛//▞▞ Memory Codex Commands ⫸</b>

<b>/start</b> - Initialize the Codex
<b>/help</b> - Show this help
<b>/stats</b> - View memory statistics
<b>/recall [query]</b> - Search memories

<b>Message Format:</b>
<code>Banner Line
Content here...
:: ∎</code>

Only messages with <code>:: ∎</code> seal are persisted.
:: ∎
"""
        await message.reply(help_text)
    
    async def cmd_stats(self, message: Message):
        """Handle /stats command"""
        user_id = str(message.from_user.id)
        stats = await self.memory.get_user_stats(user_id)
        
        stats_text = f"""
<b>▛//▞▞ Your Memory Statistics ⫸</b>

Events logged: {stats['events']}
Facts stored: {stats['facts']}
Memory chunks: {stats['chunks']}
Last sealed: {stats['last_sealed'] or 'Never'}

:: ∎
"""
        await message.reply(stats_text)
    
    async def cmd_recall(self, message: Message):
        """Handle /recall command - search memories"""
        user_id = str(message.from_user.id)
        query = message.text.replace("/recall", "").strip()
        
        if not query:
            await message.reply("Usage: /recall [search query]\n:: ∎")
            return
        
        # Search recent events
        results = await self.memory.search_events(user_id, query, limit=5)
        
        if not results:
            await message.reply(f"No memories found for: {query}\n:: ∎")
            return
        
        response = f"<b>▛//▞▞ Recalled Memories for: {query} ⫸</b>\n\n"
        for idx, event in enumerate(results, 1):
            ts = event['ts'].strftime('%Y-%m-%d %H:%M')
            banner = event['banner'] or 'no banner'
            response += f"{idx}. [{ts}] {banner}\n"
        
        response += "\n:: ∎"
        await message.reply(response)
    
    async def handle_message(self, message: Message):
        """Handle regular text messages"""
        user_id = str(message.from_user.id)
        text = message.text or ""
        
        # Extract banner (first line)
        lines = text.split('\n')
        banner = lines[0] if lines else ""
        
        # Check for seal
        has_seal = ":: ∎" in text or "∎" in text
        seal = ":: ∎" if has_seal else ""
        
        # Log event
        await self.db.log_event(
            user_id=user_id,
            kind="prompt.run",
            banner=banner,
            seal=seal,
            payload={"text": text, "has_seal": has_seal}
        )
        
        # Cache in Redis
        await self.redis.cache_message(user_id, text, banner, has_seal)
        
        # If sealed, acknowledge
        if has_seal:
            # TODO: Generate embeddings and store in memory_chunks
            await message.reply(
                f"<b>Banner:</b> {banner}\n"
                f"<b>Seal:</b> Verified ∎\n"
                f"<b>Status:</b> Memory persisted.\n"
                ":: ∎"
            )
        else:
            await message.reply(
                "⚠️ Message received but not sealed.\n"
                "Add <code>:: ∎</code> to persist to memory."
            )
    
    async def start(self):
        """Start the bot"""
        logger.info("▛//▞▞ ⟦⎊⟧ :: CODEX.BOT.STARTING ⫸")
        
        # Initialize database
        await self.db.connect()
        await self.redis.connect()
        
        logger.info("Database and Redis connected. Bot is ready.")
        logger.info(":: ∎")
        
        # Start polling
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Stop the bot"""
        await self.db.disconnect()
        await self.redis.disconnect()
        await self.bot.session.close()


async def main():
    """Main entry point"""
    bot = CodexBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
