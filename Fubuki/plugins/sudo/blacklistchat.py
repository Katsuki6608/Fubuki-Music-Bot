# All rights reserved.
#
from pyrogram.types import Message

from config import BANNED_USERS
from strings import command
from Fubuki import app
from Fubuki.misc import SUDOERS
from Fubuki.utils.database import blacklist_chat, blacklisted_chats, whitelist_chat
from Fubuki.utils.decorators.language import language


@app.on_message(command("BLACKLISTCHAT_COMMAND") & SUDOERS)
@language
async def blacklist_chat_func(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_1"])
    
    target_input = message.text.strip().split()[1]
    try:
        chat_id = int(target_input)
    except ValueError:
        return await message.reply_text(_["black_1"])

    if chat_id in await blacklisted_chats():
        return await message.reply_text(_["black_2"])
    
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        await message.reply_text(_["black_3"])
    else:
        await message.reply_text("Something went wrong.")
    
    try:
        await app.leave_chat(chat_id)
    except Exception:
        pass


@app.on_message(command("WHITELISTCHAT_COMMAND") & SUDOERS)
@language
async def white_funciton(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_4"])
    
    target_input = message.text.strip().split()[1]
    try:
        chat_id = int(target_input)
    except ValueError:
        return await message.reply_text(_["black_4"])

    if chat_id not in await blacklisted_chats():
        return await message.reply_text(_["black_5"])
    
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(_["black_6"])
    await message.reply_text("Something went wrong.")


@app.on_message(command("BLACKLISTEDCHAT_COMMAND") & ~BANNED_USERS)
@language
async def all_chats(client, message: Message, _):
    chats = await blacklisted_chats()
    if not chats:
        return await message.reply_text(_["black_8"])

    text = _["black_7"]
    count = 0
    for chat_id in chats:
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private / Inaccessible Chat"
        count += 1
        text += f"**{count}. {title}** [`{chat_id}`]\n"

    if count == 0:
        await message.reply_text(_["black_8"])
    else:
        await message.reply_text(text)
