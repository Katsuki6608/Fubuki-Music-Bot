# All rights reserved.
#

from pyrogram.types import Message

import config
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import add_off, add_on, is_on_off
from Fubuki.utils.decorators.language import language


@app.on_message(command("VIDEOMODE_COMMAND") & SUDOERS)
@language
async def videoloaymode(client, message: Message, _):
    usage = _["vidmode_1"]
    if len(message.command) != 2:
        return await message.reply_text(usage)

    state = message.text.split(None, 1)[1].strip().lower()
    target_var = getattr(config, "YTDOWNLOADER", 1)

    if state == "download":
        if await is_on_off(target_var):
            return await message.reply_text(_["vidmode_2"])
        await add_on(target_var)
        await message.reply_text(_["vidmode_2"])
    elif state == "m3u8":
        if not await is_on_off(target_var):
            return await message.reply_text(_["vidmode_3"])
        await add_off(target_var)
        await message.reply_text(_["vidmode_3"])
    else:
        await message.reply_text(usage)
