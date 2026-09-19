# All rights reserved.
#

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Union

import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from Fubuki import app

try:
    from config import lyrical
except Exception:
    lyrical = {}

try:
    from ..utils.formatters import convert_bytes, get_readable_time, seconds_to_min
except Exception:
    def convert_bytes(size: float) -> str:
        if not size:
            return "0 B"
        power = 1024
        t_n = 0
        power_labels = {0: "B", 1: "KiB", 2: "MiB", 3: "GiB", 4: "TiB"}
        while size > power:
            size /= power
            t_n += 1
        return f"{round(size, 2)} {power_labels.get(t_n, '')}"

    def get_readable_time(seconds: int) -> str:
        count = 0
        ping_time = ""
        time_list = []
        time_suffix_list = ["s", "m", "h", "days"]
        while count < 4:
            count += 1
            if count < 3:
                remainder, result = divmod(seconds, 60)
            else:
                remainder, result = divmod(seconds, 24)
            if seconds == 0 and remainder == 0:
                break
            time_list.append(int(result))
            seconds = int(remainder)
        for i in range(len(time_list)):
            time_list[i] = str(time_list[i]) + time_suffix_list[i]
        if len(time_list) == 4:
            ping_time += time_list.pop() + ", "
        time_list.reverse()
        ping_time += ":".join(time_list)
        return ping_time

    def seconds_to_min(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

try:
    from ..utils.premium import stop_btn
except Exception:
    def stop_btn(text="🚦 Cancel downloading", callback_data="stop_downloading"):
        return InlineKeyboardButton(text=text, callback_data=callback_data)

downloader = {}


class Telegram:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = getattr(config, "TELEGRAM_DOWNLOAD_EDIT_SLEEP", 3)

    async def send_split_text(self, message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x)
        return True

    async def get_link(self, message):
        if message.chat.username:
            link = f"https://t.me/{message.chat.username}/{message.reply_to_message.id}"
        else:
            xf = str(message.chat.id)[4:]
            link = f"https://t.me/c/{xf}/{message.reply_to_message.id}"
        return link

    async def get_filename(self, file, audio: Union[bool, str] = None):
        try:
            file_name = file.file_name
            if file_name is None:
                file_name = "Telegram audio file" if audio else "Telegram video file"
        except Exception:
            file_name = "Telegram audio file" if audio else "Telegram video file"
        return file_name

    async def get_duration(self, file):
        try:
            dur = seconds_to_min(file.duration)
        except Exception:
            dur = "Unknown"
        return dur

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ):
        os.makedirs("downloads", exist_ok=True)
        if audio:
            try:
                ext = "ogg" if isinstance(audio, Voice) else (audio.file_name.split(".")[-1] if audio.file_name else "mp3")
                file_name = f"{audio.file_unique_id}.{ext}"
            except Exception:
                file_name = f"{audio.file_unique_id}.ogg"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        if video:
            try:
                ext = video.file_name.split(".")[-1] if video.file_name else "mp4"
                file_name = f"{video.file_unique_id}.{ext}"
            except Exception:
                file_name = f"{video.file_unique_id}.mp4"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        return file_name

    async def is_streamable_url(self, url: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if (
                            "application/vnd.apple.mpegurl" in content_type
                            or "application/x-mpegURL" in content_type
                        ):
                            return True
                        if any(
                            keyword in content_type
                            for keyword in [
                                "audio",
                                "video",
                                "mp4",
                                "mpegurl",
                                "m3u8",
                                "mpeg",
                            ]
                        ):
                            return True
                        if url.endswith((".m3u8", ".index", ".mp4", ".mpeg", ".mpd")):
                            return True
        except Exception:
            pass
        return False

    async def download(self, _, message, mystic, fname):
        left_time = {}
        speed_counter = {}
        os.makedirs(os.path.dirname(os.path.abspath(fname)), exist_ok=True)
        if os.path.exists(fname):
            return True

        async def down_load():
            async def progress(current, total):
                if current == total:
                    return
                current_time = time.time()
                start_time = speed_counter.get(message.id, current_time)
                check_time = max(current_time - start_time, 1)
                upl = InlineKeyboardMarkup(
                    [
                        [
                            stop_btn(
                                text="🚦 Cancel downloading",
                                callback_data="stop_downloading",
                            ),
                        ]
                    ]
                )
                if datetime.now() > left_time.get(message.id, datetime.now()):
                    percentage = current * 100 / total
                    percentage = str(round(percentage, 2))
                    speed = current / check_time
                    eta = int((total - current) / max(speed, 1))
                    downloader[message.id] = eta
                    eta_str = get_readable_time(eta)
                    if not eta_str:
                        eta_str = "0 sec"
                    total_size = convert_bytes(total)
                    completed_size = convert_bytes(current)
                    speed_str = convert_bytes(speed)
                    mention = getattr(app, "mention", "Fubuki")
                    text = (
                        f"**{mention} Telegram Media Downloader**\n\n"
                        f"**Total file size:** {total_size}\n"
                        f"**Completed:** {completed_size}\n"
                        f"**Percentage:** {percentage[:5]}%\n\n"
                        f"**Speed:** {speed_str}/s\n"
                        f"**Elapsed Time:** {eta_str}"
                    )
                    try:
                        await mystic.edit_text(text, reply_markup=upl)
                    except Exception:
                        pass
                    left_time[message.id] = datetime.now() + timedelta(
                        seconds=self.sleep
                    )

            speed_counter[message.id] = time.time()
            left_time[message.id] = datetime.now()

            try:
                await app.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress,
                )
                await mystic.edit_text(
                    "Successfully Downloaded\nProcessing File Now..."
                )
                downloader.pop(message.id, None)
            except Exception:
                err_text = _["tg_2"] if isinstance(_, dict) and "tg_2" in _ else "Failed to download media from Telegram."
                await mystic.edit_text(err_text)

        if len(downloader) > 10:
            timers = []
            for x in downloader:
                timers.append(downloader[x])
            try:
                low = min(timers)
                eta = get_readable_time(low)
            except Exception:
                eta = "Unknown"
            err_limit = _["tg_1"].format(eta) if isinstance(_, dict) and "tg_1" in _ else f"Download limit exceeded. Please wait {eta}."
            await mystic.edit_text(err_limit)
            return False

        task = asyncio.create_task(down_load(), name=f"download_{message.chat.id}")
        lyrical[mystic.id] = task
        await task
        downloaded = downloader.get(message.id)
        if downloaded:
            downloader.pop(message.id)
            return False
        verify = lyrical.get(mystic.id)
        if not verify:
            return False
        lyrical.pop(mystic.id, None)
        return True
