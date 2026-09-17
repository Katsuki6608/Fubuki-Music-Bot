# Fubuki Music Bot Engine
# Channel Playback Utility - Optimized for Termux & Pyrogram 2.x

from Fubuki import app
from Fubuki.utils.database import get_cmode


async def get_channeplayCB(_, command, callback_query):
    if command == "c":
        chat_id = await get_cmode(callback_query.message.chat.id)
        if chat_id is None:
            try:
                return await callback_query.answer(_["setting_12"], show_alert=True)
            except Exception:
                return None, None
        try:
            chat = await app.get_chat(chat_id)
            channel = chat.title
        except Exception:
            try:
                return await callback_query.answer(_["cplay_4"], show_alert=True)
            except Exception:
                return None, None
    else:
        chat_id = callback_query.message.chat.id
        channel = None
    return chat_id, channel
