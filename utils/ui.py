from telegram import InlineKeyboardButton


def styled_button(text: str, callback_data: str, style: str = None, emoji_id: str = None):
    """
    Colored inline button banata hai. style: 'primary' (blue), 'success' (green), 'danger' (red).
    emoji_id: Premium animated emoji ki ID (optional) - button ke text ke pehle chhota emoji icon dikhega.
    Purane Telegram app version wale users ko yeh nahi dikhega, button normal dikhega - safe hai.
    """
    kwargs = {}
    if style:
        kwargs["style"] = style
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = emoji_id
    if kwargs:
        return InlineKeyboardButton(text, callback_data=callback_data, api_kwargs=kwargs)
    return InlineKeyboardButton(text, callback_data=callback_data)


def premium_emoji(emoji_id: str, fallback: str = "✨") -> str:
    """
    Premium animated emoji ka HTML tag banata hai message text me use karne ke liye.
    Zaroori: message bhejte waqt parse_mode="HTML" hona chahiye, aur bot owner ke
    Telegram account me Premium subscription hona chahiye, warna yeh dikhega hi nahi
    (fallback normal emoji dikh jayega).
    """
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
