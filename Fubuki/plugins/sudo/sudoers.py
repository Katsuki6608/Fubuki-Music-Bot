# All rights reserved.
#

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, MONGO_DB_URI, OWNER_ID
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import add_sudo, remove_sudo
from Fubuki.utils.decorators.language import language


@app.on_message(command("ADDSUDO_COMMAND") & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not MONGO_DB_URI:
        return await message.reply_text(
            "**Due to database settings, you cannot manage sudoers without a valid MONGO_DB_URI.**"
        )
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user_input = message.text.split(None, 1)[1].strip()
        if "@" in user_input:
            user_input = user_input.replace("@", "")
        try:
            target = int(user_input) if user_input.isdigit() else user_input
            user = await app.get_users(target)
        except Exception:
            return await message.reply_text(_["general_1"])

        if user.id in SUDOERS:
            return await message.reply_text(_["sudo_1"].format(user.mention))
        added = await add_sudo(user.id)
        if added:
            SUDOERS.add(user.id)
            await message.reply_text(_["sudo_2"].format(user.mention))
        else:
            await message.reply_text("Something went wrong.")
        return

    if not message.reply_to_message.from_user:
        return await message.reply_text(_["general_1"])

    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention

    if user_id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(mention))

    added = await add_sudo(user_id)
    if added:
        SUDOERS.add(user_id)
        await message.reply_text(_["sudo_2"].format(mention))
    else:
        await message.reply_text("Something went wrong.")


@app.on_message(command("DELSUDO_COMMAND") & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not MONGO_DB_URI:
        return await message.reply_text(
            "**Due to database settings, you cannot manage sudoers without a valid MONGO_DB_URI.**"
        )
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

        if user_id not in SUDOERS:
            return await message.reply_text(_["sudo_3"])
        removed = await remove_sudo(user_id)
        if removed:
            SUDOERS.remove(user_id)
            return await message.reply_text(_["sudo_4"])
        return await message.reply_text("Something went wrong.")

    if not message.reply_to_message.from_user:
        return await message.reply_text(_["general_1"])

    user_id = message.reply_to_message.from_user.id
    if user_id not in SUDOERS:
        return await message.reply_text(_["sudo_3"])

    removed = await remove_sudo(user_id)
    if removed:
        SUDOERS.remove(user_id)
        return await message.reply_text(_["sudo_4"])
    await message.reply_text("Something went wrong.")


@app.on_message(command("SUDOUSERS_COMMAND") & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    text = _["sudo_5"]
    count = 0
    for x in OWNER_ID:
        try:
            user = await app.get_users(x)
            user_display = user.mention if user.mention else user.first_name
            count += 1
            text += f"{count}➤ {user_display} (`{x}`)\n"
        except Exception:
            count += 1
            text += f"{count}➤ [Owner] (`{x}`)\n"

    smex = 0
    for user_id in SUDOERS:
        if user_id not in OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user_display = user.mention if user.mention else user.first_name
                if smex == 0:
                    smex += 1
                    text += _["sudo_6"]
                count += 1
                text += f"{count}➤ {user_display} (`{user_id}`)\n"
            except Exception:
                if smex == 0:
                    smex += 1
                    text += _["sudo_6"]
                count += 1
                text += f"{count}➤ [Sudo] (`{user_id}`)\n"

    if not text:
        await message.reply_text(_["sudo_7"])
    else:
        await message.reply_text(text)
