import os
import asyncio
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from converters import image_converter, document_converter, video_converter
from utils.helpers import new_session_dir, cleanup, is_file_too_big, human_size
from utils import stats
from utils.i18n import t
from utils.rate_limit import check_rate_limit
from config import MAX_FILE_SIZE_MB

# Actions jo file bhejne se pehle ek text parameter maangte hain
# (button dabane ke baad user ko text bhejna hai, tab file maangi jaayegi)
PARAM_PROMPTS = {
    "action_img_resize": ("resize_dims", "Naya size batao, format: `800x600` (width x height)."),
    "action_pdf_add_password": ("add_password_pwd", "Woh password batao jo PDF pe lagana hai."),
    "action_pdf_remove_password": ("remove_password_pwd", "PDF ka current password batao."),
}

# Actions jo seedhe file maangte hain (koi param nahi chahiye)
DIRECT_PROMPTS = {
    "action_img_to_jpg": "Ab woh image bhejo jise JPG banana hai.",
    "action_img_to_png": "Ab woh image bhejo jise PNG banana hai.",
    "action_img_to_webp": "Ab woh image bhejo jise WEBP banana hai.",
    "action_img_compress": "Ab woh image bhejo jiska size chhota karna hai.",
    "action_img_to_pdf": "Ab ek ya ek se zyada images bhejo (last me /done bhejna).",
    "action_pdf_to_img": "Ab woh PDF bhejo jise images me convert karna hai.",
    "action_pdf_to_text": "Ab woh PDF bhejo jiska text nikalna hai.",
    "action_text_to_pdf": "Ab woh .txt file bhejo jise PDF banana hai.",
    "action_pdf_to_word": "Ab woh PDF bhejo jise Word (.docx) banana hai.",
    "action_word_to_pdf": "Ab woh .docx file bhejo jise PDF banana hai.",
    "action_pdf_merge": "Ab 2 ya zyada PDFs bhejo (last me /done bhejna).",
    "action_pdf_split": "Ab woh PDF bhejo jise split karna hai.",
    "action_excel_to_csv": "Ab woh .xlsx file bhejo jise CSV banana hai.",
    "action_csv_to_excel": "Ab woh .csv file bhejo jise Excel banana hai.",
    "action_vid_to_audio": "Ab woh video bhejo jiska audio nikalna hai.",
    "action_vid_compress": "Ab woh video bhejo jiska size chhota karna hai.",
}


async def _get_incoming_file(update: Update):
    """Photo, document, video ya audio -> ek common Telegram File object return karta hai."""
    msg = update.message
    if msg.document:
        return msg.document.file_id, msg.document.file_name, msg.document.file_size
    if msg.photo:
        largest = msg.photo[-1]
        return largest.file_id, f"{largest.file_id}.jpg", largest.file_size
    if msg.video:
        return msg.video.file_id, msg.video.file_name or f"{msg.video.file_id}.mp4", msg.video.file_size
    if msg.audio:
        return msg.audio.file_id, msg.audio.file_name or f"{msg.audio.file_id}.mp3", msg.audio.file_size
    return None, None, None


async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = stats.get_language(user_id)

    action = context.user_data.get("pending_action")
    if not action:
        await update.message.reply_text(t("no_pending_action", lang))
        return

    allowed, wait_seconds = check_rate_limit(user_id)
    if not allowed:
        await update.message.reply_text(t("rate_limited", lang, seconds=wait_seconds))
        return

    file_id, file_name, file_size = await _get_incoming_file(update)
    if not file_id:
        await update.message.reply_text(t("unsupported_file", lang))
        return

    if file_size and is_file_too_big(file_size):
        await update.message.reply_text(
            t("file_too_big", lang, size=human_size(file_size), limit=MAX_FILE_SIZE_MB)
        )
        return

    session_dir = new_session_dir()
    input_path = os.path.join(session_dir, file_name)

    status_msg = await update.message.reply_text(t("processing", lang))

    try:
        tg_file = await context.bot.get_file(file_id)
        await tg_file.download_to_drive(input_path)

        # ---------- IMAGES → IMAGES ----------
        if action in ("action_img_to_jpg", "action_img_to_png", "action_img_to_webp"):
            fmt = {"action_img_to_jpg": "jpg", "action_img_to_png": "png", "action_img_to_webp": "webp"}[action]
            output_path = os.path.join(session_dir, f"converted.{fmt}")
            await asyncio.to_thread(image_converter.convert_image_format, input_path, output_path, fmt)
            await update.message.reply_document(document=open(output_path, "rb"), filename=f"converted.{fmt}")

        elif action == "action_img_compress":
            output_path = os.path.join(session_dir, "compressed.jpg")
            await asyncio.to_thread(image_converter.compress_image, input_path, output_path, quality=50)
            before, after = human_size(file_size), human_size(os.path.getsize(output_path))
            await update.message.reply_document(document=open(output_path, "rb"),
                                                  filename="compressed.jpg",
                                                  caption=f"Size: {before} → {after}")

        elif action == "action_img_resize":
            width, height = context.user_data.get("resize_dims", (800, 600))
            ext = os.path.splitext(file_name)[1] or ".png"
            output_path = os.path.join(session_dir, f"resized{ext}")
            await asyncio.to_thread(image_converter.resize_image, input_path, output_path, width, height)
            await update.message.reply_document(document=open(output_path, "rb"),
                                                  filename=f"resized{ext}")

        # ---------- IMAGES → PDF (multi-image collection) ----------
        elif action == "action_img_to_pdf":
            context.user_data.setdefault("collected_images", []).append(input_path)
            context.user_data["img_to_pdf_dir"] = session_dir
            await status_msg.edit_text(
                f"✅ Image add ho gayi ({len(context.user_data['collected_images'])} total). "
                "Aur images bhejo, ya sab ho gaya toh /done bhejo."
            )
            return

        # ---------- PDF MERGE (multi-pdf collection) ----------
        elif action == "action_pdf_merge":
            context.user_data.setdefault("collected_pdfs", []).append(input_path)
            context.user_data["pdf_merge_dir"] = session_dir
            await status_msg.edit_text(
                f"✅ PDF add ho gayi ({len(context.user_data['collected_pdfs'])} total). "
                "Aur PDFs bhejo, ya sab ho gaya toh /done bhejo."
            )
            return

        # ---------- PDF SPLIT (file pehle, range baad me) ----------
        elif action == "action_pdf_split":
            total_pages = await asyncio.to_thread(document_converter.get_page_count, input_path)
            context.user_data["split_pdf_path"] = input_path
            context.user_data["split_pdf_dir"] = session_dir
            context.user_data["awaiting_param"] = "split_range"
            await status_msg.edit_text(
                f"✅ PDF me {total_pages} pages hain. Ab range bhejo, jaise `2-5`."
            )
            return

        # ---------- PDF PASSWORD ----------
        elif action == "action_pdf_add_password":
            password = context.user_data.get("add_password_pwd", "")
            output_path = os.path.join(session_dir, "protected.pdf")
            await asyncio.to_thread(document_converter.add_pdf_password, input_path, output_path, password)
            await update.message.reply_document(document=open(output_path, "rb"), filename="protected.pdf")

        elif action == "action_pdf_remove_password":
            password = context.user_data.get("remove_password_pwd", "")
            output_path = os.path.join(session_dir, "unlocked.pdf")
            await asyncio.to_thread(document_converter.remove_pdf_password, input_path, output_path, password)
            await update.message.reply_document(document=open(output_path, "rb"), filename="unlocked.pdf")

        # ---------- PDF → IMAGES ----------
        elif action == "action_pdf_to_img":
            image_paths = await asyncio.to_thread(image_converter.pdf_to_images, input_path, session_dir)
            if len(image_paths) == 1:
                await update.message.reply_document(document=open(image_paths[0], "rb"))
            else:
                media = [InputMediaPhoto(open(p, "rb")) for p in image_paths[:10]]
                await update.message.reply_media_group(media=media)
                if len(image_paths) > 10:
                    await update.message.reply_text(f"Total {len(image_paths)} pages the, sirf pehle 10 bheje.")

        # ---------- DOCUMENT CONVERSIONS ----------
        elif action == "action_pdf_to_text":
            output_path = os.path.join(session_dir, "converted.txt")
            await asyncio.to_thread(document_converter.pdf_to_text, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.txt")

        elif action == "action_text_to_pdf":
            output_path = os.path.join(session_dir, "converted.pdf")
            await asyncio.to_thread(document_converter.text_to_pdf, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.pdf")

        elif action == "action_pdf_to_word":
            output_path = os.path.join(session_dir, "converted.docx")
            await asyncio.to_thread(document_converter.pdf_to_word, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.docx")

        elif action == "action_word_to_pdf":
            output_path = os.path.join(session_dir, "converted.pdf")
            await asyncio.to_thread(document_converter.word_to_pdf, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.pdf")

        # ---------- EXCEL / CSV ----------
        elif action == "action_excel_to_csv":
            output_path = os.path.join(session_dir, "converted.csv")
            await asyncio.to_thread(document_converter.excel_to_csv, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.csv")

        elif action == "action_csv_to_excel":
            output_path = os.path.join(session_dir, "converted.xlsx")
            await asyncio.to_thread(document_converter.csv_to_excel, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.xlsx")

        # ---------- VIDEO/AUDIO ----------
        elif action == "action_vid_to_audio":
            output_path = os.path.join(session_dir, "converted.mp3")
            await asyncio.to_thread(video_converter.video_to_audio, input_path, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="converted.mp3")

        elif action == "action_vid_compress":
            output_path = os.path.join(session_dir, "compressed.mp4")
            await asyncio.to_thread(video_converter.compress_video, input_path, output_path)
            before, after = human_size(file_size), human_size(os.path.getsize(output_path))
            await update.message.reply_document(document=open(output_path, "rb"),
                                                  filename="compressed.mp4",
                                                  caption=f"Size: {before} → {after}")

        stats.log_feature_use(user_id, action)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(t("conversion_failed", lang, error=str(e)[:200]))
    finally:
        if action not in ("action_img_to_pdf", "action_pdf_merge", "action_pdf_split"):
            cleanup(session_dir)
            context.user_data.pop("pending_action", None)
            context.user_data.pop("resize_dims", None)
            context.user_data.pop("split_range", None)
            context.user_data.pop("add_password_pwd", None)
            context.user_data.pop("remove_password_pwd", None)


async def text_param_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Jab user resize dimensions, PDF page range, ya password type karta hai
    (button dabane ke baad), yeh handler usko process karta hai.
    """
    awaiting = context.user_data.get("awaiting_param")
    if not awaiting:
        return  # Normal text message hai, kuch nahi karna

    user_id = update.effective_user.id
    lang = stats.get_language(user_id)
    text = update.message.text.strip()

    if awaiting == "get_emoji_id":
        context.user_data["awaiting_param"] = None
        entities = update.message.entities or []
        emoji_ids = [e.custom_emoji_id for e in entities if e.type == "custom_emoji"]
        if not emoji_ids:
            await update.message.reply_text(
                "❌ Koi custom emoji nahi mila is message me. Emoji picker se select karke bhejna hai, "
                "keyboard se type kiya normal emoji kaam nahi karega."
            )
        else:
            ids_text = "\n".join(f"`{eid}`" for eid in emoji_ids)
            await update.message.reply_text(f"✅ Emoji ID(s) mil gayi:\n{ids_text}", parse_mode="Markdown")
        return

    if awaiting == "resize_dims":
        try:
            width_str, height_str = text.lower().replace(" ", "").split("x")
            width, height = int(width_str), int(height_str)
            if width <= 0 or height <= 0 or width > 8000 or height > 8000:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Sahi format me bhejo, jaise: `800x600`")
            return
        context.user_data["resize_dims"] = (width, height)
        context.user_data["pending_action"] = "action_img_resize"
        context.user_data["awaiting_param"] = None
        await update.message.reply_text(f"✅ Size set: {width}x{height}. Ab image bhejo.")
        return

    if awaiting == "split_range":
        try:
            start_str, end_str = text.replace(" ", "").split("-")
            start, end = int(start_str), int(end_str)
        except ValueError:
            await update.message.reply_text("❌ Sahi format me bhejo, jaise: `2-5`")
            return

        input_path = context.user_data.get("split_pdf_path")
        session_dir = context.user_data.get("split_pdf_dir")
        if not input_path or not session_dir:
            await update.message.reply_text("Session expire ho gaya, phir se /start karo.")
            return

        try:
            output_path = os.path.join(session_dir, "split.pdf")
            await asyncio.to_thread(document_converter.split_pdf, input_path, output_path, start, end)
            await update.message.reply_document(document=open(output_path, "rb"), filename="split.pdf")
            stats.log_feature_use(user_id, "action_pdf_split")
        except Exception as e:
            await update.message.reply_text(f"❌ Split me error: {str(e)[:200]}")
        finally:
            cleanup(session_dir)
            context.user_data.pop("pending_action", None)
            context.user_data.pop("awaiting_param", None)
            context.user_data.pop("split_pdf_path", None)
            context.user_data.pop("split_pdf_dir", None)
        return

    if awaiting == "add_password_pwd":
        context.user_data["add_password_pwd"] = text
        context.user_data["pending_action"] = "action_pdf_add_password"
        context.user_data["awaiting_param"] = None
        await update.message.reply_text("✅ Password set ho gaya. Ab PDF bhejo.")
        return

    if awaiting == "remove_password_pwd":
        context.user_data["remove_password_pwd"] = text
        context.user_data["pending_action"] = "action_pdf_remove_password"
        context.user_data["awaiting_param"] = None
        await update.message.reply_text("✅ Password set ho gaya. Ab PDF bhejo.")
        return


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Multi-image → PDF ya Multi-PDF → Merge collection ko finalize karta hai."""
    action = context.user_data.get("pending_action")

    if action == "action_pdf_merge":
        pdfs = context.user_data.get("collected_pdfs", [])
        session_dir = context.user_data.get("pdf_merge_dir")
        if len(pdfs) < 2:
            await update.message.reply_text("Kam se kam 2 PDFs bhejo merge karne ke liye.")
            return
        try:
            output_path = os.path.join(session_dir, "merged.pdf")
            await asyncio.to_thread(document_converter.merge_pdfs, pdfs, output_path)
            await update.message.reply_document(document=open(output_path, "rb"), filename="merged.pdf")
            stats.log_feature_use(update.effective_user.id, "action_pdf_merge")
        except Exception as e:
            await update.message.reply_text(f"❌ Merge me error: {str(e)[:200]}")
        finally:
            cleanup(session_dir)
            context.user_data.pop("pending_action", None)
            context.user_data.pop("collected_pdfs", None)
            context.user_data.pop("pdf_merge_dir", None)
        return

    # Default: images → pdf
    images = context.user_data.get("collected_images", [])
    session_dir = context.user_data.get("img_to_pdf_dir")

    if not images:
        await update.message.reply_text("Koi file collect nahi hui. Pehle files bhejo.")
        return

    try:
        output_path = os.path.join(session_dir, "converted.pdf")
        await asyncio.to_thread(image_converter.images_to_pdf, images, output_path)
        await update.message.reply_document(document=open(output_path, "rb"), filename="converted.pdf")
        stats.log_feature_use(update.effective_user.id, "action_img_to_pdf")
    except Exception as e:
        await update.message.reply_text(f"❌ PDF banane me error: {str(e)[:200]}")
    finally:
        cleanup(session_dir)
        context.user_data.pop("pending_action", None)
        context.user_data.pop("collected_images", None)
        context.user_data.pop("img_to_pdf_dir", None)
        
