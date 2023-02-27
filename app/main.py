from telegram.ext import ApplicationBuilder, CommandHandler, filters, MessageHandler

from src import Config, handlers


if __name__ == "__main__":
    cfg = Config()
    application = ApplicationBuilder().token(cfg.api_key).build()

    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(CommandHandler('help', handlers.hlp))
    application.add_handler(CommandHandler('source', handlers.source_url))
    application.add_handler(CommandHandler('set', handlers.set_alerts))
    application.add_handler(CommandHandler('check', handlers.check_alerts))
    application.add_handler(CommandHandler('cancel', handlers.cancel_alerts))
    application.add_handler(MessageHandler(filters.COMMAND, handlers.unknown))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.unknown_text))

    application.run_polling()
