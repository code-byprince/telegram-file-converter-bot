from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import stats
from utils.i18n import t
from utils.ui import premium_emoji
from config import WELCOME_EMOJI_ID


def main_menu_keyboard(lang: str = "hi"):
    from handlers.callback_handler import main_menu_buttons
    return InlineKeyboardMarkup(main_menu_buttons(lang))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    stats.log_user(user.id, user.username, user.first_name)

    lang = stats.get_language(user.id)

    # Agar WELCOME_EMOJI_ID set hai (.env me), toh pehle ek chhota animated emoji bhejte hain.
    # Yeh alag message me isliye hai kyunki emoji ke liye HTML parse_mode chahiye,
    # jabki neeche wala welcome text Markdown me hai - dono ek saath mix nahi ho sakte.
    if WELCOME_EMOJI_ID:
        try:
            await update.message.reply_text(premium_emoji(WELCOME_EMOJI_ID), parse_mode="HTML")
        except Exception:
            pass  # Emoji fail ho (jaise Premium na ho), toh bhi normal welcome message aa jaye

    await update.message.reply_text(
        t("welcome", lang), parse_mode="Markdown", reply_markup=main_menu_keyboard(lang)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bas /start bhejo, category choose karo, phir file bhejo.\n"
        f"Max file size: {context.bot_data.get('max_size_mb', 20)}MB.\n\n"
        "Commands: /start /help /done /history /language /stats (admin only)"
    )
    
