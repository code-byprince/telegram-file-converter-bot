from telegram import Update, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from handlers.file_handler import PARAM_PROMPTS, DIRECT_PROMPTS
from utils import stats
from utils.i18n import t
from utils.ui import styled_button

# style=None matlab default/white button, "primary"=blue, "success"=green, "danger"=red
IMAGE_MENU = [
    [styled_button("→ JPG", "action_img_to_jpg", "primary"),
     styled_button("→ PNG", "action_img_to_png", "success")],
    [styled_button("→ WEBP", "action_img_to_webp", "primary"),
     styled_button("Compress", "action_img_compress", "success")],
    [styled_button("Resize", "action_img_resize", "primary")],
    [styled_button("Images → PDF", "action_img_to_pdf", "success")],
    [styled_button("PDF → Images", "action_pdf_to_img", "primary")],
    [styled_button("⬅️ Back", "menu_main", "primary")],
]

DOCUMENT_MENU = [
    [styled_button("PDF → Text", "action_pdf_to_text", "success"),
     styled_button("Text → PDF", "action_text_to_pdf", "primary")],
    [styled_button("PDF → Word", "action_pdf_to_word", "success"),
     styled_button("Word → PDF", "action_word_to_pdf", "primary")],
    [styled_button("Merge PDFs", "action_pdf_merge", "success"),
     styled_button("Split PDF", "action_pdf_split", "primary")],
    [styled_button("🔒 Add Password", "action_pdf_add_password", "success"),
     styled_button("🔓 Remove Password", "action_pdf_remove_password", "danger")],
    [styled_button("⬅️ Back", "menu_main", "primary")],
]

EXCEL_MENU = [
    [styled_button("Excel → CSV", "action_excel_to_csv", "primary")],
    [styled_button("CSV → Excel", "action_csv_to_excel", "success")],
    [styled_button("⬅️ Back", "menu_main", "primary")],
]

VIDEO_MENU = [
    [styled_button("Video → MP3", "action_vid_to_audio", "primary")],
    [styled_button("Video Compress", "action_vid_compress", "success")],
    [styled_button("⬅️ Back", "menu_main", "success")],
]


def main_menu_buttons(lang: str = "hi"):
    """main_menu_keyboard yahi use karta hai."""
    return [
        [styled_button(t("menu_image", lang), "menu_image", "primary")],
        [styled_button(t("menu_document", lang), "menu_document", "primary")],
        [styled_button(t("menu_excel", lang), "menu_excel", "success")],
        [styled_button(t("menu_video", lang), "menu_video", "primary")],
    ]


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest:
        # Bot Render pe "so" raha tha, callback bahut der se process hua aur
        # Telegram ka query expire ho gaya - ignore karo, button ka kaam phir bhi ho jayega
        pass
    data = query.data

    if data == "menu_main":
        from handlers.start import main_menu_keyboard
        context.user_data.clear()
        lang = stats.get_language(update.effective_user.id)
        await query.edit_message_text(t("welcome", lang), parse_mode="Markdown",
                                       reply_markup=main_menu_keyboard(lang))
        return

    if data == "menu_image":
        await query.edit_message_text("🖼️ *Image Tools* — kya karna hai?", parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(IMAGE_MENU))
        return

    if data == "menu_document":
        await query.edit_message_text("📄 *Document Tools* — kya karna hai?", parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(DOCUMENT_MENU))
        return

    if data == "menu_excel":
        await query.edit_message_text("📊 *Excel/CSV Tools* — kya karna hai?", parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(EXCEL_MENU))
        return

    if data == "menu_video":
        await query.edit_message_text("🎬 *Video/Audio Tools* — kya karna hai?", parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(VIDEO_MENU))
        return

    # Actions jo pehle text parameter maangte hain (resize dims, password, split range)
    if data in PARAM_PROMPTS:
        param_key, prompt_text = PARAM_PROMPTS[data]
        context.user_data["awaiting_param"] = param_key
        context.user_data["pending_action"] = None
        await query.edit_message_text(f"✍️ {prompt_text}")
        return

    # Actions jo seedhe file maangte hain
    if data in DIRECT_PROMPTS:
        context.user_data["pending_action"] = data
        context.user_data["awaiting_param"] = None
        context.user_data["collected_images"] = []
        context.user_data["collected_pdfs"] = []
        await query.edit_message_text(f"✅ {DIRECT_PROMPTS[data]}")
        return
        
