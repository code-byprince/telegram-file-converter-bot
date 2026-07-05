from telegram import Update
from telegram.ext import ContextTypes

from utils import stats
from config import ADMIN_ID

FEATURE_LABELS = {
    "action_img_to_jpg": "Image → JPG",
    "action_img_to_png": "Image → PNG",
    "action_img_to_webp": "Image → WEBP",
    "action_img_compress": "Image Compress",
    "action_img_to_pdf": "Images → PDF",
    "action_pdf_to_img": "PDF → Images",
    "action_pdf_to_text": "PDF → Text",
    "action_text_to_pdf": "Text → PDF",
    "action_pdf_to_word": "PDF → Word",
    "action_word_to_pdf": "Word → PDF",
    "action_vid_to_audio": "Video → Audio",
    "action_vid_compress": "Video Compress",
    "action_img_resize": "Image Resize",
    "action_pdf_merge": "PDF Merge",
    "action_pdf_split": "PDF Split",
    "action_pdf_add_password": "PDF Add Password",
    "action_pdf_remove_password": "PDF Remove Password",
    "action_excel_to_csv": "Excel → CSV",
    "action_csv_to_excel": "CSV → Excel",
}


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_ID or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Yeh command sirf admin ke liye hai.")
        return

    data = stats.get_stats()
    lines = [
        "📊 *Bot Stats*",
        f"👥 Total Users: {data['total_users']}",
        f"🔄 Total Conversions: {data['total_conversions']}",
        f"🟢 Aaj Active: {data['active_today']}",
        "",
        "*Feature-wise usage:*",
    ]
    if data["feature_breakdown"]:
        for feature, count in data["feature_breakdown"]:
            label = FEATURE_LABELS.get(feature, feature)
            lines.append(f"• {label}: {count}")
    else:
        lines.append("Abhi tak koi conversion nahi hua.")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def getemojiid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin ko premium/custom emoji ki ID nikalne me help karta hai.
    Kaam kaise: /getemojiid bhejo, phir jis message me woh custom emoji hai
    (khud bheja ya kisi channel se copy-paste/forward kiya), woh bot ko bhej do.
    """
    if not ADMIN_ID or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Yeh command sirf admin ke liye hai.")
        return
    context.user_data["awaiting_param"] = "get_emoji_id"
    await update.message.reply_text(
        "✍️ Ab isi chat me neeche emoji picker (😊 icon) khol ke, jo bhi custom/premium "
        "emoji chahiye woh dhoondh ke daal do aur bhej do.\n\n"
        "⚠️ Zaroori: sirf apne Telegram ke emoji picker se select karke bhejna hai — "
        "copy-paste ya forward karne se ID nahi milegi, entity data chala jata hai."
    )
    
