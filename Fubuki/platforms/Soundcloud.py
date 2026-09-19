# All rights reserved.
#

import asyncio
import os
from typing import Tuple, Union

from yt_dlp import YoutubeDL

try:
    from Fubuki.utils.decorators import asyncify
except Exception:
    def asyncify(func):
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper

try:
    from Fubuki.utils.formatters import seconds_to_min
except Exception:
    def seconds_to_min(seconds):
        if not seconds:
            return "00:00"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


class SoundCloud:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
            "quiet": True,
            "no_warnings": True,
        }

    async def valid(self, link: str) -> bool:
        return "soundcloud" in link

    @asyncify
    def track(self, url: str) -> Tuple[Union[dict, None], Union[str, None]]:
        with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception:
                return None, None
            duration_min = seconds_to_min(info.get("duration", 0))
            track_details = {
                "title": info.get("title", "SoundCloud Track"),
                "link": url,
                "vidid": info.get("id", ""),
                "duration_sec": info.get("duration", 0),
                "duration_min": duration_min,
                "uploader": info.get("uploader", "SoundCloud"),
                "thumb": info.get("thumbnail", ""),
            }
            return track_details, info.get("id", "")

    @asyncify
    def download(self, url: str) -> Union[Tuple[dict, str], bool]:
        os.makedirs("downloads", exist_ok=True)
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(url)
            except Exception:
                return False
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            duration_min = seconds_to_min(info.get("duration", 0))
            track_details = {
                "title": info.get("title", "SoundCloud Track"),
                "duration_sec": info.get("duration", 0),
                "duration_min": duration_min,
                "uploader": info.get("uploader", "SoundCloud"),
                "filepath": xyz,
            }
            return track_details, xyz
