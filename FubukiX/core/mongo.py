# All rights reserved.
#

from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from pyrogram import Client

import config

from ..logging import LOGGER


DB_NAME = "Fubuki"

if config.MONGO_DB_URI is None:
    LOGGER(__name__).warning(
        "No MONGO_DB_URI found in config. Please provide your own MongoDB URI to avoid data loss."
    )
    temp_client = Client(
        "Fubuki",
        bot_token=config.BOT_TOKEN,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
    )
    temp_client.start()
    info = temp_client.get_me()
    username = info.username
    temp_client.stop()
    raise SystemExit("Error: MONGO_DB_URI is required. Please set it in config.py or .env file.")
else:
    _mongo_async_ = _mongo_client_(config.MONGO_DB_URI)
    _mongo_sync_ = MongoClient(config.MONGO_DB_URI)
    mongodb = _mongo_async_[DB_NAME]
    pymongodb = _mongo_sync_[DB_NAME]
