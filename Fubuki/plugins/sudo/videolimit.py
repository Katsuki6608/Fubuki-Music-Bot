# All rights reserved.
#

from pyrogram.types import Message

from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import set_video_limit
from Fubuki.utils.decorators.language import language


@app.on_message(command("VIDEOLIMIT_COMMAND") & SUDOERS)
@language
async def set_video_limit_kid(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["vid_1"])

    state = message.text.split(None, 1)[1].strip()

    if state.lower() == "disable":
        await set_video_limit(0)
        return await message.reply_text(_["vid_4"])

    if state.isdigit():
        limit = int(state)
        await set_video_limit(limit)
        if limit == 0:
            return await message.reply_text(_["vid_4"])
        return await message.reply_text(_["vid_3"].format(limit))

    return await message.reply_text(_["vid_2"])
