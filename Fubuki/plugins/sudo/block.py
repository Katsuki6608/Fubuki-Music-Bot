# All rights reserved.
#

from pyrogram.types import Message

from config import BANNED_USERS, OWNER_ID
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import add_gban_user, remove_gban_user
from Fubuki.utils.decorators.language import language


@app.on_message(command("BLOCK_COMMAND") & SUDOERS)
@language
async def useradd(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user_input = message.text.split(None, 1)[1].strip()
        if "@" in user_input:
            user_input = user_input.replace("@", "")
        try:
            target = int(user_input) if user_input.isdigit() else user_input
            user = await app.get_users(target)
            user_id = user.id
            mention = user.mention
        except Exception:
            return await message.reply_text(_["general_1"])
    else:
        if not message.reply_to_message.from_user:
            return await message.reply_text(_["general_1"])
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention

    if user_id == app.id or user_id in OWNER_ID:
        return await message.reply_text("You cannot block the Bot or the Owner.")

    if user_id in BANNED_USERS:
        return await message.reply_text(_["block_1"].format(mention))

    await add_gban_user(user_id)
    BANNED_USERS.add(user_id)
    await message.reply_text(_["block_2"].format(mention))


@app.on_message(command("UNBLOCK_COMMAND") & SUDOERS)
@language
async def userdel(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user_input = message.text.split(None, 1)[1].strip()
        if "@" in user_input:
            user_input = user_input.replace("@", "")
        try:
            target = int(user_input) if user_input.isdigit() else user_input
            user = await app.get_users(target)
            user_id = user.id
        except Exception:
            return await message.reply_text(_["general_1"])
    else:
        if not message.reply_to_message.from_user:
            return await message.reply_text(_["general_1"])
        user_id = message.reply_to_message.from_user.id

    if user_id not in BANNED_USERS:
        return await message.reply_text(_["block_3"])

    await remove_gban_user(user_id)
    BANNED_USERS.remove(user_id)
    await message.reply_text(_["block_4"])


@app.on_message(command("BLOCKED_COMMAND") & SUDOERS)
@language
async def sudoers_list(client, message: Message, _):
    if not BANNED_USERS:
        return await message.reply_text(_["block_5"])
    mystic = await message.reply_text(_["block_6"])
    msg = _["block_7"]
    count = 0
    for user_id in list(BANNED_USERS):
        try:
            user = await app.get_users(user_id)
            user_display = user.mention if user.mention else user.first_name
            count += 1
            msg += f"{count}➤ {user_display} (`{user_id}`)\n"
        except Exception:
            count += 1
            msg += f"{count}➤ [Banned User] (`{user_id}`)\n"

    if count == 0:
        return await mystic.edit_text(_["block_5"])
    await mystic.edit_text(msg)
