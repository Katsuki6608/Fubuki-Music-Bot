# All rights reserved.
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from Fubuki import HELPABLE, LOGGER, app, userbot
from Fubuki.core.call import Fubuki_Call as Ayush
from Fubuki.plugins import ALL_MODULES
from Fubuki.utils.database import get_banned_users, get_gbanned
from Fubuki.utils.premium import install_text_entities_patch, validate_db

install_text_entities_patch()


async def init():
    if len(config.STRING_SESSIONS) == 0:
        LOGGER("Fubuki").error(
            "No Assistant Clients Vars Defined!.. Exiting Process."
        )
        return

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()
    LOGGER("Fubuki").info("Validating premium emoji database...")
    try:
        await validate_db(app)
    except Exception:
        LOGGER("Fubuki").warning("Could not validate premium emoji database.")

    for all_module in ALL_MODULES:
        imported_module = importlib.import_module(all_module)

        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    LOGGER("Fubuki.plugins").info("Successfully Imported All Modules")

    await userbot.start()
    await Ayush.start()
    LOGGER("Fubuki").info("Assistant Started Successfully")

    try:
        await Ayush.stream_call(
            "https://telegra.ph/file/2e4d0e980f7690680a653.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("Fubuki").error(
            "Please ensure the voice call in your log group is active."
        )
        exit()
    except Exception:
        pass

    LOGGER("Fubuki").info("Fubuki Started Successfully")
    await idle()
    await app.stop()
    await userbot.stop()


if __name__ == "__main__":
    app.run(init())
    LOGGER("Fubuki").info("Stopping Fubuki! GoodBye")
