import logging
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from raven.config import load_settings
from raven.memory import MemoryStore
from raven.backends.openai_backend import OpenAIBackend
from raven.backends.n8n_backend import N8nBackend
from raven.backends.relay_backend import RelayBackend


logger = logging.getLogger(__name__)


def _user_allowed(user_id: int, allowed_csv: Optional[str]) -> bool:
    if not allowed_csv:
        return True
    try:
        allowed = {int(x.strip()) for x in allowed_csv.split(",") if x.strip()}
    except ValueError:
        return True
    return user_id in allowed


def _choose_backend(name: str):
    name = (name or "openai").lower()
    if name == "openai":
        return OpenAIBackend()
    if name == "n8n":
        return N8nBackend()
    if name == "relay":
        return RelayBackend()
    return OpenAIBackend()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    user = update.effective_user
    if not user or not _user_allowed(user.id, settings.allowed_user_ids):
        return
    await update.message.reply_text(
        "Raven online. Send a message to chat. Use /backend openai|n8n|relay, /clear to reset."
    )


async def backend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    user = update.effective_user
    chat = update.effective_chat
    if not (user and chat and update.message):
        return
    if not _user_allowed(user.id, settings.allowed_user_ids):
        return

    mem = MemoryStore(settings.db_path)
    await mem.initialize()

    if not context.args:
        current = await mem.get_backend(chat.id)
        await update.message.reply_text(f"Current backend: {current or settings.default_backend}")
        return

    name = context.args[0].lower()
    if name not in {"openai", "n8n", "relay"}:
        await update.message.reply_text("Unknown backend. Choose from openai, n8n, relay.")
        return

    await mem.set_backend(chat.id, name)
    await update.message.reply_text(f"Backend set to {name}")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    user = update.effective_user
    chat = update.effective_chat
    if not (user and chat and update.message):
        return
    if not _user_allowed(user.id, settings.allowed_user_ids):
        return

    mem = MemoryStore(settings.db_path)
    await mem.initialize()
    await mem.clear_history(chat.id)
    await update.message.reply_text("History cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = load_settings()
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if not (user and chat and message and message.text):
        return
    if not _user_allowed(user.id, settings.allowed_user_ids):
        return

    mem = MemoryStore(settings.db_path)
    await mem.initialize()

    # Determine backend for this chat
    backend_name = await mem.get_backend(chat.id) or settings.default_backend
    backend = _choose_backend(backend_name)

    await mem.append_message(chat.id, "user", message.text)
    history = await mem.get_history(chat.id, limit=20)

    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    reply_text = await backend.generate_reply(chat.id, history, message.text, settings)

    if reply_text:
        await mem.append_message(chat.id, "assistant", reply_text)
        await message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


def build_application(settings) -> Application:
    application: Application = ApplicationBuilder().token(settings.telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("backend", backend))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application


def run_polling() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    application = build_application(settings)
    logger.info("Raven bot started (polling)")
    application.run_polling()


def run_webhook() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not settings.webhook_url:
        raise RuntimeError("WEBHOOK_URL is not set")

    application = build_application(settings)
    logger.info("Raven bot started (webhook)")
    application.run_webhook(
        listen="0.0.0.0",
        port=settings.port,
        url_path="/",
        webhook_url=settings.webhook_url,
    )


def main() -> None:
    settings = load_settings()
    if settings.use_webhook:
        run_webhook()
    else:
        run_polling()


if __name__ == "__main__":
    main()
