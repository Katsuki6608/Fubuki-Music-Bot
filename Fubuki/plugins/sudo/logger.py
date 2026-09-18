# All rights reserved.
#

from pyrogram.types import Message

import config
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import add_off, add_on, is_on_off
from Fubuki.utils.decorators.language import language


@app.on_message(command("LOGGER_COMMAND") & SUDOERS)
@language
async def logger(client, message: Message, _):
    usage = _["log_1"]
    if len(message.command) != 2:
        return await message.reply_text(usage)

    state = message.text.split(None, 1)[1].strip().lower()

    if state == "enable":
        if await is_on_off(config.LOG):
            return await message.reply_text(_["log_2"])
        await add_on(config.LOG)
        await message.reply_text(_["log_2"])
    elif state == "disable":
        if not await is_on_off(config.LOG):
            return await message.reply_text(_["log_3"])
        await add_off(config.LOG)
        await message.reply_text(_["log_3"])
    else:
        await message.reply_text(usage)
