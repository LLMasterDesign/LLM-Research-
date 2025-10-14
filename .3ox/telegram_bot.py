#!/usr/bin/env python3
"""
NOCTUA Telegram Bot Integration
Allows mobile access to NOCTUA through Telegram
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Telegram bot library
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  python-telegram-bot not available")
    print("   Install: pip install python-telegram-bot")

# TOML config
try:
    import tomli as toml
except ImportError:
    try:
        import tomllib as toml
    except ImportError:
        print("❌ Install tomli: pip install tomli")
        sys.exit(1)

# Import owl for continuity
sys.path.insert(0, str(Path(__file__).parent))
try:
    from owl import NoctuaOwl
except ImportError:
    print("❌ owl.py not found")
    sys.exit(1)


class NoctuaTelegramBot:
    """Telegram interface for NOCTUA"""
    
    def __init__(self, config_path: str = ".3ox/config.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Check if enabled
        if not self.config['telegram']['enabled']:
            raise ValueError("Telegram integration is disabled in config.toml")
        
        # Check token
        self.token = self.config['telegram'].get('token', '')
        if not self.token:
            raise ValueError("Telegram bot token not configured")
        
        # Allowed users
        self.allowed_users = set(self.config['telegram'].get('allowed_users', []))
        
        # Initialize owl
        self.owl = NoctuaOwl(config_path)
        
        # Build application
        if TELEGRAM_AVAILABLE:
            self.app = Application.builder().token(self.token).build()
            self._setup_handlers()
    
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'rb') as f:
            return toml.load(f)
    
    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        if not self.allowed_users:
            return True  # Allow all if no restrictions
        return user_id in self.allowed_users
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        
        # Commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("memory", self.cmd_memory))
        self.app.add_handler(CommandHandler("set", self.cmd_set))
        self.app.add_handler(CommandHandler("get", self.cmd_get))
        self.app.add_handler(CommandHandler("blocks", self.cmd_blocks))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        
        # Message handler for conversations
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user = update.effective_user
        
        if not self._is_authorized(user.id):
            await update.message.reply_text("❌ Unauthorized. Contact admin.")
            return
        
        await update.message.reply_text(
            f"🦉 *NOCTUA Active*\n\n"
            f"Hello {user.first_name}!\n"
            f"I'm your continuity agent with persistent memory.\n\n"
            f"Node ID: `{self.owl.node_id[:16]}...`\n"
            f"Use /help for available commands.",
            parse_mode='Markdown'
        )
        
        self.owl.log_history("telegram", f"User {user.id} started bot")
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        # Get stats
        memory_count = self.owl.db.cursor().execute(
            "SELECT COUNT(*) FROM mem WHERE node = ?", (self.owl.node_id,)
        ).fetchone()[0]
        
        history_count = self.owl.db.cursor().execute(
            "SELECT COUNT(*) FROM history WHERE node = ?", (self.owl.node_id,)
        ).fetchone()[0]
        
        blocks_count = self.owl.db.cursor().execute(
            "SELECT COUNT(*) FROM folder_blocks WHERE node = ?", (self.owl.node_id,)
        ).fetchone()[0]
        
        redis_status = "✅ Connected" if self.owl.redis else "⚠️  Offline"
        
        await update.message.reply_text(
            f"📊 *NOCTUA Status*\n\n"
            f"🆔 Node: `{self.owl.node_id[:24]}...`\n"
            f"💾 Memory Keys: {memory_count}\n"
            f"📜 History Items: {history_count}\n"
            f"🧩 Folder Blocks: {blocks_count}\n"
            f"🔴 Redis: {redis_status}\n"
            f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            parse_mode='Markdown'
        )
    
    async def cmd_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List memory keys"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        cur = self.owl.db.cursor()
        cur.execute("""
            SELECT k, v, updated_at 
            FROM mem 
            WHERE node = ? 
            ORDER BY updated_at DESC 
            LIMIT 10
        """, (self.owl.node_id,))
        
        rows = cur.fetchall()
        
        if not rows:
            await update.message.reply_text("📝 No memory keys stored yet.")
            return
        
        lines = ["📝 *Recent Memory Keys*\n"]
        for k, v, ts in rows:
            value_preview = v[:40] + "..." if len(v) > 40 else v
            lines.append(f"• `{k}`: {value_preview}")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
    
    async def cmd_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set memory key: /set key value"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /set <key> <value>")
            return
        
        key = context.args[0]
        value = " ".join(context.args[1:])
        
        self.owl.set_memory(key, value)
        await update.message.reply_text(f"✅ Set `{key}` = {value[:50]}...", parse_mode='Markdown')
    
    async def cmd_get(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get memory key: /get key"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /get <key>")
            return
        
        key = context.args[0]
        value = self.owl.get_memory(key)
        
        if value:
            await update.message.reply_text(f"📝 `{key}` = {value}", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Key `{key}` not found", parse_mode='Markdown')
    
    async def cmd_blocks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List folder blocks"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        blocks = self.owl.get_folder_blocks()
        
        if not blocks:
            await update.message.reply_text("🧩 No folder blocks created yet.")
            return
        
        lines = [f"🧩 *Folder Blocks* ({len(blocks)})\n"]
        for block in blocks[:10]:
            icon = {'config': '⚙️', 'data': '📦', 'task': '✅', 'telegram': '💬'}.get(block['block_type'], '📁')
            lines.append(f"{icon} `{block['id'][:8]}` - {block['block_type']}")
            lines.append(f"   📂 {block['folder_path']}")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        await update.message.reply_text(
            "🦉 *NOCTUA Commands*\n\n"
            "/start - Initialize bot\n"
            "/status - Show system status\n"
            "/memory - List recent memory keys\n"
            "/set <key> <value> - Store memory\n"
            "/get <key> - Retrieve memory\n"
            "/blocks - List folder blocks\n"
            "/help - Show this help\n\n"
            "Send any message to log it in history.",
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        user = update.effective_user
        text = update.message.text
        
        # Log to history
        self.owl.log_history("user", f"[Telegram:{user.first_name}] {text}")
        
        # Simple acknowledgment
        await update.message.reply_text(
            f"📝 Logged to history.\n"
            f"Use /memory to see stored data."
        )
    
    async def run(self):
        """Run the bot"""
        if not TELEGRAM_AVAILABLE:
            print("❌ python-telegram-bot not installed")
            return
        
        print("=" * 60)
        print(f"🦉 NOCTUA Telegram Bot Starting...")
        print(f"🆔 Node: {self.owl.node_id[:32]}...")
        print(f"👥 Allowed Users: {len(self.allowed_users) if self.allowed_users else 'All'}")
        print("=" * 60)
        
        # Start polling
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        print("✅ Bot is running. Press Ctrl+C to stop.")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
        finally:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            self.owl.shutdown()


def main():
    """Main entry point"""
    try:
        bot = NoctuaTelegramBot()
        asyncio.run(bot.run())
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To enable Telegram:")
        print("   1. Create a bot with @BotFather on Telegram")
        print("   2. Edit .3ox/config.toml:")
        print("      [telegram]")
        print("      enabled = true")
        print("      token = \"YOUR_BOT_TOKEN\"")
        print("      allowed_users = [123456789]  # Optional")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
