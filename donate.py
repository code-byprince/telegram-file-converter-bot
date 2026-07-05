from telegram import Update, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes

from utils import stats
from utils.access import has_access
from utils.ui import styled_button

STAR_OPTIONS = [5, 10, 50, 100, 500]


def unlock_keyboard():
    keyboard = [
        [styled_button(f"⭐ {amount} Stars", f"donate_{amount}", "success")]
        for amount in STAR_OPTIONS
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_paywall(message):
    """Jab user unlocked nahi hai, tab yeh message dikhta hai. `message` koi bhi object ho sakta hai jisme reply_text ho."""
    await message.reply_text(
        "🔒 *Bot use karne ke liye pehle ek chhota sa donation karo*\n\n"
        "Bas 5 ya 10 ⭐ Stars donate karo, bot turant unlock ho jayega — "
        "yeh ek baar ka support hai, dobara nahi maangenge!\n\n"
        "Neeche se amount choose karo 👇",
        parse_mode="Markdown",
        reply_markup=unlock_keyboard(),
    )


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❤️ Agar yeh bot tumhare kaam aaya, toh Telegram Stars se support kar sakte ho!\n\n"
        "Kitne Stars donate karna chahoge?",
        reply_markup=unlock_keyboard(),
    )


async def donate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    amount = int(query.data.split("_")[1])

    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title="Bot Support Donation",
        description=f"File Converter Bot ko support karne ke liye {amount} Stars ka chhota sa donation. Dhanyawad! 🙏",
        payload=f"donation_{amount}_stars",
        provider_token="",  # Telegram Stars ke liye khaali rehta hai
        currency="XTR",
        prices=[LabeledPrice(label=f"{amount} Stars Donation", amount=amount)],
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Payment confirm hone se pehle Telegram yeh puchta hai - hamesha 10 second ke andar reply karna zaroori hai."""
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Payment successful hone ke baad access unlock karta hai aur thank you message bhejta hai."""
    payment = update.message.successful_payment
    amount = payment.total_amount  # XTR ke liye yeh seedha stars count hota hai
    user_id = update.effective_user.id

    stats.log_feature_use(user_id, f"donation_{amount}_stars")

    was_locked = not has_access(user_id)
    stats.mark_user_paid(user_id)

    if was_locked:
        from handlers.start import main_menu_keyboard
        lang = stats.get_language(user_id)
        await update.message.reply_text(
            f"🙏 Dhanyawad! {amount} ⭐ Stars mile — bot ab **unlock** ho gaya hai!\n\n"
            "Neeche se category choose karo 👇",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(lang),
        )
    else:
        await update.message.reply_text(
            f"🙏 Dhanyawad! Tumne {amount} ⭐ Stars donate kiye. "
            "Tumhari support se yeh bot free aur behtar bana rahega!"
        )
