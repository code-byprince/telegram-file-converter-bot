from telegram import Update
from telegram.ext import ContextTypes

from utils import stats
from utils.i18n import t
from handlers.admin import FEATURE_LABELS


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = stats.get_language(user_id)
    rows = stats.get_history(user_id, limit=5)

    if not rows:
        await update.message.reply_text(t("history_empty", lang))
        return

    lines = [t("history_title", lang, count=len(rows)), ""]
    for feature, used_at in rows:
        label = FEATURE_LABELS.get(feature, feature)
        time_part = used_at.split("T")[1][:5] if "T" in used_at else used_at
        date_part = used_at.split("T")[0]
        lines.append(f"• {label} — {date_part} {time_part}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
