# All rights reserved.
#

import asyncio

from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import BANNED_USERS
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils import get_readable_time
from Fubuki.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from Fubuki.utils.decorators.language import language


@app.on_message(command("GBAN_COMMAND") & SUDOERS)
@language
async def gbanuser(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user_input = message.text.split(None, 1)[1].strip()
        try:
            user_target = int(user_input) if user_input.isdigit() or (user_input.startswith("-") and user_input[1:].isdigit()) else user_input
            user = await app.get_users(user_target)
            user_id = user.id
            mention = user.mention
        except Exception:
            return await message.reply_text(_["general_1"])
    else:
        if not message.reply_to_message.from_user:
            return await message.reply_text(_["general_1"])
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention

    if user_id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user_id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user_id in SUDOERS:
        return await message.reply_text(_["gban_3"])

    is_gbanned = await is_banned_user(user_id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(mention))

    if user_id not in BANNED_USERS:
        BANNED_USERS.add(user_id)

    chats = await get_served_chats()
    served_chats = [int(chat["chat_id"]) for chat in chats if "chat_id" in chat]

    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_5"].format(mention, time_expected))

    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user_id)
            number_of_chats += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass

    await add_banned_user(user_id)
    await message.reply_text(_["gban_6"].format(mention, number_of_chats))
    try:
        await mystic.delete()
    except Exception:
        pass


@app.on_message(command("UNGBAN_COMMAND") & SUDOERS)
@language
async def gungabn(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user_input = message.text.split(None, 1)[1].strip()
        try:
            user_target = int(user_input) if user_input.isdigit() or (user_input.startswith("-") and user_input[1:].isdigit()) else user_input
            user = await app.get_users(user_target)
            user_id = user.id
            mention = user.mention
        except Exception:
            return await message.reply_text(_["general_1"])
    else:
        if not message.reply_to_message.from_user:
            return await message.reply_text(_["general_1"])
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention

    is_gbanned = await is_banned_user(user_id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(mention))

    if user_id in BANNED_USERS:
        BANNED_USERS.remove(user_id)

    chats = await get_served_chats()
    served_chats = [int(chat["chat_id"]) for chat in chats if "chat_id" in chat]

    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_8"].format(mention, time_expected))

    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user_id)
            number_of_chats += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass

    await remove_banned_user(user_id)
    await message.reply_text(_["gban_9"].format(mention, number_of_chats))
    try:
        await mystic.delete()
    except Exception:
        pass


@app.on_message(command("GBANNED_COMMAND") & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])

    mystic = await message.reply_text(_["gban_11"])
    msg = "Gbanned Users:\n\n"
    count = 0
    users = await get_banned_users()

    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user_display = user.mention if user.mention else user.first_name
            msg += f"{count}➤ {user_display}\n"
        except Exception:
            msg += f"{count}➤ [Unfetched User] {user_id}\n"

    if count == 0:
        return await mystic.edit_text(_["gban_10"])
    return await mystic.edit_text(msg)
