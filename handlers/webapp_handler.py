import json
from telegram import Update
from telegram.ext import ContextTypes

from utils import stats
from utils.access import has_access
from handlers.file_handler import PARAM_PROMPTS, DIRECT_PROMPTS


async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab user Mini App (Web App) me button dabata hai, yeh data yahan aata hai."""
    user_id = update.effective_user.id

    if not has_access(user_id):
        from handlers.donate import send_paywall
        await send_paywall(update.message)
        return

    try:
        data = json.loads(update.effective_message.web_app_data.data)
        action = data.get("action")
    except Exception:
        await update.message.reply_text("❌ Kuch galat data mila, dobara try karo.")
        return

    context.user_data.clear()

    if action in PARAM_PROMPTS:
        param_key, prompt_text = PARAM_PROMPTS[action]
        context.user_data["awaiting_param"] = param_key
        context.user_data["pending_action"] = None
        await update.message.reply_text(f"✍️ {prompt_text}")
        return

    if action in DIRECT_PROMPTS:
        context.user_data["pending_action"] = action
        context.user_data["awaiting_param"] = None
        context.user_data["collected_images"] = []
        context.user_data["collected_pdfs"] = []
        await update.message.reply_text(f"✅ {DIRECT_PROMPTS[action]}")
        return

    await update.message.reply_text("❌ Yeh action pehchana nahi gaya.")
