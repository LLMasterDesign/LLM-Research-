import logging
from datetime import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from .config import Settings
from .state import StateStore
from .phames import infer_bias, is_four_hour_long, is_four_hour_short
from .portfolio import Portfolio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mission-bot')

MISSION_PATH = 'data/mission_state.json'

BADASS_PREFIX = "[MISSION COMMANDER] "
STYLE = (
    "Discipline over dopamine. We execute the plan. "
    "No mid-flight changes. Respect your risk."
)

portfolio = Portfolio()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(BADASS_PREFIX + "Ready. Feed me Phames analysis or set mission.")


async def set_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store = StateStore(MISSION_PATH)
    state = store.reset_if_new_day()
    if state.locked:
        await update.message.reply_text(BADASS_PREFIX + "Mission already locked. No changes mid-day.")
        return
    text = ' '.join(context.args) if context.args else ''
    if not text:
        await update.message.reply_text("Usage: /goal <reason or plan>")
        return
    bias = infer_bias(text)
    if is_four_hour_long(text) and bias == 'short':
        bias = 'long'
    state.bias = bias
    state.reason = text
    store.save(state)
    await update.message.reply_text(BADASS_PREFIX + f"Mission primed: bias={state.bias}. Say /lock when ready.\n{STYLE}")


async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store = StateStore(MISSION_PATH)
    state = store.reset_if_new_day()
    if state.locked:
        await update.message.reply_text(BADASS_PREFIX + "Already locked. Eyes on the plan.")
        return
    state.locked = True
    store.save(state)
    await update.message.reply_text(BADASS_PREFIX + f"Locked: {state.bias}. No deviations today.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store = StateStore(MISSION_PATH)
    state = store.reset_if_new_day()
    await update.message.reply_text(BADASS_PREFIX + f"Day {state.day} | bias={state.bias} | locked={state.locked}\n{state.reason}")


async def set_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /pos <SYMBOL> <AMOUNT>")
        return
    sym, amt = context.args[0].upper(), float(context.args[1])
    portfolio.set(sym, amt)
    await update.message.reply_text(BADASS_PREFIX + f"Position set: {sym} {amt}")


async def value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        total = portfolio.total_value_usd()
        await update.message.reply_text(BADASS_PREFIX + f"Portfolio value: ${total:,.2f}")
    except Exception as e:
        await update.message.reply_text(BADASS_PREFIX + f"Price fetch error: {e}")


async def echo_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    settings = Settings.from_env()
    chat_id_str = str(update.effective_chat.id) if update.effective_chat else ''

    # Only watch configured chats; ignore DMs or other groups
    if settings.phames_chat_id and chat_id_str != settings.phames_chat_id and chat_id_str != settings.mission_chat_id:
        return

    text = update.message.text
    store = StateStore(MISSION_PATH)
    state = store.reset_if_new_day()

    # If mission is not locked and Phames speaks, prime or lock mission
    if not state.locked:
        # Only trust Phames user if configured
        author_username = (update.effective_user.username or '').lower() if update.effective_user else ''
        configured_phames = (settings.phames_username or '').lstrip('@').lower()
        if configured_phames and author_username != configured_phames:
            return
        bias = infer_bias(text)
        if is_four_hour_long(text) and bias == 'short':
            bias = 'long'
        state.bias = bias
        state.reason = text[:500]
        if settings.auto_lock:
            state.locked = True
        store.save(state)
        if settings.auto_lock:
            await update.message.reply_text(BADASS_PREFIX + f"Locked in from analysis: {state.bias}. {STYLE}")
        else:
            await update.message.reply_text(BADASS_PREFIX + f"Primed from analysis: {state.bias}. Say /lock to commit. {STYLE}")
        return

    # Enforce rules during the day
    four_long = is_four_hour_long(text)
    four_short = is_four_hour_short(text)
    if four_long and state.bias == 'short':
        await update.message.reply_text(BADASS_PREFIX + "4H long detected. Standing down from shorts.")
    if four_short and state.bias == 'long':
        await update.message.reply_text(BADASS_PREFIX + "4H short noted. Maintain discipline; reassess only tomorrow.")


async def daily_checkin(context: ContextTypes.DEFAULT_TYPE) -> None:
    store = StateStore(MISSION_PATH)
    state = store.reset_if_new_day()
    chat_id = context.job.chat_id if context.job else None
    thread_id = None
    if context.job and context.job.data and isinstance(context.job.data, dict):
        thread_id = context.job.data.get('thread_id')
    msg = BADASS_PREFIX + f"New day. Bias={state.bias}. {STYLE}"
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=msg, message_thread_id=thread_id)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start, /goal <text>, /lock, /status, /pos <sym> <amt>, /value"
    )


def _parse_chat_id(raw: str) -> int | None:
    try:
        raw = str(raw).strip()
        if not raw:
            return None
        return int(raw)
    except Exception:
        return None


def run() -> None:
    settings = Settings.from_env()
    app = Application.builder().token(settings.telegram_token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('goal', set_goal))
    app.add_handler(CommandHandler('lock', lock))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('pos', set_portfolio))
    app.add_handler(CommandHandler('value', value))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_analyze))

    mission_chat = _parse_chat_id(settings.mission_chat_id)
    if mission_chat is not None:
        app.job_queue.run_daily(
            daily_checkin,
            time=time(hour=0, minute=0),
            chat_id=mission_chat,
            name='daily_checkin',
            data={'thread_id': settings.mission_thread_id},
        )

    app.run_polling(close_loop=False)


if __name__ == '__main__':
    run()
