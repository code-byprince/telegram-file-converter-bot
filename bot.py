import logging
import threading

from flask import Flask
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler,
)

from config import BOT_TOKEN, PORT, MAX_FILE_SIZE_MB
from handlers.start import start_command, help_command
from handlers.callback_handler import button_handler
from handlers.file_handler import file_handler, done_command, text_param_handler
from handlers.admin import stats_command, getemojiid_command
from handlers.language import language_command, language_callback
from handlers.history import history_command
from handlers.donate import (
    donate_command, donate_callback, precheckout_callback, successful_payment_callback,
)
from handlers.webapp_handler import web_app_data_handler
from utils import stats as stats_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    """Koi bhi unhandled error aaye toh bot crash na ho, bas log ho jaye."""
    logger.error("Exception aayi update handle karte waqt:", exc_info=context.error)

# ---------- Flask (Render free plan ko "alive" dikhane ke liye + Mini App serve karne ke liye) ----------
flask_app = Flask(__name__, static_folder="webapp", static_url_path="/webapp")


@flask_app.route("/")
def health():
    return "File Converter Bot is running ✅"


@flask_app.route("/webapp")
def webapp_redirect():
    return flask_app.send_static_file("index.html")


def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)


# ---------- Telegram Bot ----------
def main():
    stats_db.init_db()

    application = Application.builder().token(BOT_TOKEN).build()
    application.bot_data["max_size_mb"] = MAX_FILE_SIZE_MB

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("done", done_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("getemojiid", getemojiid_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("donate", donate_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(donate_callback, pattern="^donate_"))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO,
        file_handler,
    ))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_param_handler,
    ))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot polling shuru ho raha hai...")
    application.run_polling(allowed_updates=["message", "callback_query", "pre_checkout_query"])


if __name__ == "__main__":
    # Flask ek background thread me chalega (Render health check ke liye),
    # aur Telegram bot main thread me polling karega.
    threading.Thread(target=run_flask, daemon=True).start()
    main()
