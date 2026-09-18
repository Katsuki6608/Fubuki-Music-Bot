# All rights reserved.
#

from pyrogram.types import Message

import config
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import (
    add_private_chat,
    get_private_served_chats,
    is_served_private_chat,
    remove_private_chat,
)
from Fubuki.utils.decorators.language import language


def is_pbot_enabled():
    val = getattr(config, "PRIVATE_BOT_MODE", None)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ["true", "yes", "1", "on"]
    return False


@app.on_message(command("AUTHORIZE_COMMAND") & SUDOERS)
@language
async def authorize(client, message: Message, _):
    if not is_pbot_enabled():
        return await message.reply_text(_["pbot_12"])
    if len(message.command) != 2:
        return await message.reply_text(_["pbot_1"])
    try:
        chat_id = int(message.text.strip().split()[1])
    except Exception:
        return await message.reply_text(_["pbot_7"])
    if not await is_served_private_chat(chat_id):
        await add_private_chat(chat_id)
        await message.reply_text(_["pbot_3"])
    else:
        await message.reply_text(_["pbot_5"])


@app.on_message(command("UNAUTHORIZE_COMMAND") & SUDOERS)
@language
async def unauthorize(client, message: Message, _):
    if not is_pbot_enabled():
        return await message.reply_text(_["pbot_12"])
    if len(message.command) != 2:
        return await message.reply_text(_["pbot_2"])
    try:
        chat_id = int(message.text.strip().split()[1])
    except Exception:
        return await message.reply_text(_["pbot_7"])
    if not await is_served_private_chat(chat_id):
        return await message.reply_text(_["pbot_6"])
    else:
        await remove_private_chat(chat_id)
        return await message.reply_text(_["pbot_4"])


@app.on_message(command("AUTHORIZED_COMMAND") & SUDOERS)
@language
async def authorized(client, message: Message, _):
    if not is_pbot_enabled():
        return await message.reply_text(_["pbot_12"])
    m = await message.reply_text(_["pbot_8"])
    chats = await get_private_served_chats()
    if not chats:
        return await m.edit(_["pbot_11"])

    served_chats = [int(chat["chat_id"]) for chat in chats if "chat_id" in chat]
    text = _["pbot_9"]
    count = 0
    co = 0
    msg = _["pbot_13"]

    for served_chat in served_chats:
        try:
            chat_obj = await app.get_chat(served_chat)
            title = chat_obj.title or "Unknown Title"
            count += 1
            text += f"{count}:- {title[:15]} [{served_chat}]\n"
        except Exception:
            title = _["pbot_10"]
            co += 1
            msg += f"{co}:- {title} [{served_chat}]\n"

    final_text = ""
    if co == 0:
        if count == 0:
            return await m.edit(_["pbot_11"])
        final_text = text
    else:
        if count == 0:
            final_text = msg
        else:
            final_text = f"{text}\n{msg}"

    if len(final_text) > 4096:
        final_text = final_text[:4090] + "..."
    await m.edit(final_text)
