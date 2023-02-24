from telegram import Update
from telegram.ext import ContextTypes

from src import getLogger
from src.commons import get_tomorrow_9am_cet
from src.open_meteo import report_weather

log = getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Hello! Welcome to the Bot. Please write /help to see the commands available.",
    )


async def hlp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=(
            "Available Commands:\n"
            "/source - To get the Bot source code URL\n"
            "/weather - To get current weather in Amsterdam\n"
            "/set - Set alerting to receive weather everyday at 9am CET\n"
            "/check - Check whether you are subscribed for alerts\n"
            "/cancel - Cancel your alerting subscription if any\n"
        ),
    )


async def source_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Bot source code is here https://github.com/NikiforovG/weather_alerting_bot/",
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Sorry '{update.message.text}' is not a valid command"  # type: ignore
    )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=f"Sorry I can't recognize you, you said '{update.message.text}'",  # type: ignore
    )


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sending a weather alert"""
    chat_id = update.effective_message.chat_id  # type: ignore
    message = report_weather()
    await context.bot.send_message(chat_id=chat_id, text=message)
    log.info("id %s: weather update sent", chat_id)


async def alert_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Trigger sending a weather alert and schedule next alert"""
    await weather(update, context)
    chat_id = update.effective_message.chat_id  # type: ignore
    due = get_tomorrow_9am_cet()
    context.job_queue.run_once(weather, when=due, chat_id=chat_id, name=str(chat_id))  # type: ignore
    log.info("id %s: new alert scheduled", chat_id)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)  # type: ignore
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
        log.info("id %s: current jobs removed", name)
    return True


async def set_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Setup alerting"""
    chat_id = update.effective_message.chat_id  # type: ignore

    job_removed = remove_job_if_exists(str(chat_id), context)
    due = get_tomorrow_9am_cet()
    context.job_queue.run_once(alert_weather, when=due, chat_id=chat_id, name=str(chat_id))  # type: ignore

    text = "Alerting successfully set!"
    if job_removed:
        text += " And old one was removed."
    await update.effective_message.reply_text(text)  # type: ignore
    log.info("id %s: alerting set", chat_id)


async def check_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check existing alerting"""
    chat_id = update.effective_message.chat_id  # type: ignore
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))  # type: ignore

    if alerting_set := (len(current_jobs) > 0):
        text = "You are subscribed for weather alerting."
    else:
        text = "You don't have any set weather alerting."
    await update.effective_message.reply_text(text)  # type: ignore
    log.info("id %s: alerting checked, result: %s", chat_id, alerting_set)


async def cancel_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel alerting"""
    chat_id = update.effective_message.chat_id  # type: ignore
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))  # type: ignore

    if alerting_set := (len(current_jobs) > 0):
        text = "Your weather alerting is cancelled."
        remove_job_if_exists(str(chat_id), context)
    else:
        text = "You don't have any set weather alerting."
    await update.effective_message.reply_text(text)  # type: ignore
    log.info("id %s: alerting cancelled, alerting was active: %s", chat_id, alerting_set)
