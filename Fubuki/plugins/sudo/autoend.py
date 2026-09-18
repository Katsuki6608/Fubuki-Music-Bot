# All rights reserved.
#

from pyrogram.types import Message

from strings import command, get_string
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import autoend_off, autoend_on, get_lang, is_autoend


@app.on_message(command("AUTOEND_COMMAND") & SUDOERS)
async def auto_end_stream(client, message: Message):
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except Exception:
        _ = get_string("en")

    usage = "**ᴜsᴀɢᴇ:**\n\n/autoend [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)

    state = message.text.split(None, 1)[1].strip().lower()

    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "Auto End Stream Enabled.\n\nBot will automatically leave the voice chat after 3 minutes if nobody is listening."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("Auto End Stream Disabled.")
    else:
        await message.reply_text(usage)
