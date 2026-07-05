STRINGS = {
    "welcome": {
        "hi": (
            "👋 *Namaste! Main File Converter Bot hoon.*\n\n"
            "Main yeh sab kar sakta hoon:\n"
            "🖼️ Image ↔ Image, Compress, Resize, PDF↔Image\n"
            "📄 PDF ↔ Word, Text ↔ PDF, Merge/Split, Password\n"
            "📊 Excel ↔ CSV\n"
            "🎬 Video → Audio, Video Compress\n\n"
            "Neeche se category choose karo 👇"
        ),
        "en": (
            "👋 *Hi! I'm your File Converter Bot.*\n\n"
            "Here's what I can do:\n"
            "🖼️ Image ↔ Image, Compress, Resize, PDF↔Image\n"
            "📄 PDF ↔ Word, Text ↔ PDF, Merge/Split, Password\n"
            "📊 Excel ↔ CSV\n"
            "🎬 Video → Audio, Video Compress\n\n"
            "Choose a category below 👇"
        ),
    },
    "menu_image": {"hi": "🖼️ Image Tools", "en": "🖼️ Image Tools"},
    "menu_document": {"hi": "📄 Document Tools", "en": "📄 Document Tools"},
    "menu_video": {"hi": "🎬 Video/Audio Tools", "en": "🎬 Video/Audio Tools"},
    "menu_excel": {"hi": "📊 Excel/CSV Tools", "en": "📊 Excel/CSV Tools"},
    "back": {"hi": "⬅️ Peeche", "en": "⬅️ Back"},
    "processing": {"hi": "⏳ Processing... thoda wait karo.", "en": "⏳ Processing... please wait."},
    "no_pending_action": {
        "hi": "Pehle /start bhejo aur category choose karo, tab file bhejo.",
        "en": "Send /start first and choose a category, then send your file.",
    },
    "unsupported_file": {"hi": "Yeh file type support nahi hai.", "en": "This file type isn't supported."},
    "file_too_big": {
        "hi": "⚠️ File bahut badi hai ({size}). Max limit: {limit}MB (free hosting resource limit).",
        "en": "⚠️ File is too large ({size}). Max limit: {limit}MB (free hosting resource limit).",
    },
    "conversion_failed": {"hi": "❌ Conversion fail ho gaya: {error}", "en": "❌ Conversion failed: {error}"},
    "rate_limited": {
        "hi": "⏱️ Bahut fast bhej rahe ho! {seconds} second ruk ke phir try karo.",
        "en": "⏱️ Sending too fast! Wait {seconds} seconds and try again.",
    },
    "lang_choose": {
        "hi": "Apni language choose karo:",
        "en": "Choose your language:",
    },
    "lang_set": {
        "hi": "✅ Language Hindi (Hinglish) set ho gayi.",
        "en": "✅ Language set to English.",
    },
    "history_empty": {
        "hi": "Abhi tak koi conversion nahi hui hai.",
        "en": "No conversions yet.",
    },
    "history_title": {
        "hi": "🕘 *Tumhari last {count} conversions:*",
        "en": "🕘 *Your last {count} conversions:*",
    },
}


def t(key: str, lang: str = "hi", **kwargs) -> str:
    """Given key aur language ke hisaab se translated text return karta hai."""
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("hi") or key
    if kwargs:
        text = text.format(**kwargs)
    return text
