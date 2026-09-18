# All rights reserved.
#
import asyncio
import sys

from pyrogram import Client
from pyrogram.errors import ChatWriteForbidden, UserAlreadyParticipant
import config

from ..logging import LOGGER

assistants = []
assistantids = []


class Userbot(Client):
    def __init__(self):
        self.clients = []
        self.sessions = [s for s in config.STRING_SESSIONS if s and s.strip()]

        for i, session in enumerate(self.sessions, start=1):
            client = Client(
                f"FubukiString{i}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                in_memory=True,
                no_updates=True,
                session_string=session.strip(),
            )
            self.clients.append(client)
            # Dynamic numbering support (userbot.one, userbot.two, etc.)
            num_words = ["one", "two", "three", "four", "five"]
            if i <= len(num_words):
                setattr(self, num_words[i - 1], client)

    async def _start(self, client, index):
        LOGGER(__name__).info(f"Starting Assistant Client #{index}")
        try:
            await client.start()
            assistants.append(index)
            get_me = await client.get_me()
            client.username = get_me.username or ""
            client.id = get_me.id
            client.mention = get_me.mention
            assistantids.append(get_me.id)
            client.name = f"{get_me.first_name} {get_me.last_name or ''}".strip()

            assistant_msg = f"""
╔══════════════════════╗
  🤖 **ᴀssɪsᴛᴀɴᴛ sᴛᴀʀᴛᴇᴅ** 🤖
╚══════════════════════╝

┌──────────────────────┐
│ 🧑 **ɴᴀᴍᴇ :** {client.name}
│ 🔑 **ɪᴅ :** <code>{client.id}</code>
│ 🔗 **ᴜsᴇʀɴᴀᴍᴇ :** @{client.username}
│ 🔢 **ɪɴsᴛᴀɴᴄᴇ :** #{index}
│ 📡 **sᴛᴀᴛᴜs :** ✅ ᴀᴄᴛɪᴠᴇ
│ 🎵 **ʀᴏʟᴇ :** ᴠᴏɪᴄᴇᴄʜᴀᴛ ᴀssɪsᴛᴀɴᴛ
└──────────────────────┘

⚡ **ʀᴇᴀᴅʏ ᴛᴏ ᴊᴏɪɴ ᴠᴏɪᴄᴇᴄʜᴀᴛs**
💎 **ᴘʀᴇᴍɪᴜᴍ sᴛʀᴇᴀᴍɪɴɢ ᴀᴄᴛɪᴠᴇ**
"""
            if config.LOGGER_ID:
                try:
                    await client.send_message(config.LOGGER_ID, assistant_msg)
                except ChatWriteForbidden:
                    try:
                        await client.join_chat(config.LOGGER_ID)
                        await client.send_message(config.LOGGER_ID, assistant_msg)
                    except UserAlreadyParticipant:
                        pass
                    except Exception as err:
                        LOGGER(__name__).warning(
                            f"Assistant Account #{index} could not post in Log Group: {err}"
                        )
                except Exception as err:
                    LOGGER(__name__).warning(
                        f"Assistant Account #{index} log message failed: {err}"
                    )

        except Exception as e:
            LOGGER(__name__).error(
                f"Assistant Account #{index} failed with error: {str(e)}."
            )
            sys.exit(1)

    async def start(self):
        if not self.clients:
            LOGGER(__name__).error("No assistant sessions configured.")
            return
        tasks = [self._start(client, i) for i, client in enumerate(self.clients, start=1)]
        await asyncio.gather(*tasks)

    async def stop(self):
        tasks = [client.stop() for client in self.clients if client.is_connected]
        if tasks:
            await asyncio.gather(*tasks)

    def __getattr__(self, name):
        if not self.clients:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        first_client = self.clients[0]
        if hasattr(first_client, name):
            return getattr(first_client, name)
        raise AttributeError(f"'{type(first_client).__name__}' object has no attribute '{name}'")
