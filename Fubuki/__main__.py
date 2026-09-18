import importlib
import asyncio
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from VenomX import HELPABLE, LOGGER, app, userbot
from VenomX.core.call import Ayush
from VenomX.plugins import ALL_MODULES
from VenomX.utils.database import get_banned_users, get_gbanned
from VenomX.utils.premium import install_text_entities_patch, validate_db

# Failover Manager import
from failover import FailoverManager

install_text_entities_patch()

failover = FailoverManager()

async def renew_lease_worker():
    """Background task to keep extending Redis lock while running."""
    while True:
        await asyncio.sleep(20)
        success = failover.renew_lease()
        if not success:
            LOGGER("Failover").error("Lost Redis lease lock! Stopping bot instance...")
            await app.stop()
            await userbot.stop()
            break

async def start_engine():
    if len(config.STRING_SESSIONS) == 0:
        LOGGER("VenomX").error(
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
    LOGGER("VenomX").info("Validating premium emoji database...")
    try:
        await validate_db(app)
    except Exception:
        LOGGER("VenomX").warning("Could not validate premium emoji database.")
    for all_module in ALL_MODULES:
        imported_module = importlib.import_module(all_module)

        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    LOGGER("VenomX.plugins").info("Successfully Imported All Modules ")
    await userbot.start()
    await Ayush.start()
    LOGGER("VenomX").info("Assistant Started Successfully")
    try:
        await Ayush.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("VenomX").error(
            "Please ensure the voice call in your log group is active."
        )
        exit()

    LOGGER("VenomX").info("VenomX Started Successfully")
    
    # Start the lease renew background task
    asyncio.create_task(renew_lease_worker())
    
    await idle()
    await app.stop()
    await userbot.stop()

async def main_loop():
    LOGGER("Failover").info("Waiting for cluster leader election...")
    while True:
        if failover.acquire_lock():
            LOGGER("Failover").info("Acquired cluster lock! Launching bot...")
            try:
                await start_engine()
            finally:
                failover.release_lock()
            break
        else:
            LOGGER("Failover").info("Another node is active. Running on STANDBY mode...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_loop())
    LOGGER("VenomX").info("Stopping VenomX! GoodBye")
