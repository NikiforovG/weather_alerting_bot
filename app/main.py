import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler

from src.config import Config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Hello! Welcome to the Bot. Please write /help to see the commands available.",
    )


async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Available Commands :\n/source - To get the Bot source code URL",
    )


async def source_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Bot source code is here https://github.com/NikiforovG/weather_alerting_bot/tree/master",
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Sorry '{update.message.text}' is not a valid command"  # type: ignore
    )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=f"Sorry I can't recognize you , you said '{update.message.text}'",
    )


if __name__ == "__main__":
    cfg = Config()
    application = ApplicationBuilder().token(cfg.api_key).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', _help))
    application.add_handler(CommandHandler('source', source_url))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), unknown_text))

    application.run_polling()
