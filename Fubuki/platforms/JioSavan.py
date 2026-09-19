# All rights reserved.
#

import asyncio
import os
from io import BytesIO
from typing import Tuple, Union

import aiohttp
import yt_dlp

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from config import seconds_to_time
except Exception:
    def seconds_to_time(seconds):
        if not seconds:
            return "00:00"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

try:
    from Fubuki.utils.decorators import asyncify
except Exception:
    def asyncify(func):
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper


class Saavn:

    @staticmethod
    async def valid(url: str) -> bool:
        return "jiosaavn.com" in url

    @staticmethod
    async def is_song(url: str) -> bool:
        return "song" in url and not "/featured/" in url and "/album/" not in url

    @staticmethod
    async def is_playlist(url: str) -> bool:
        return "/featured/" in url or "/album" in url

    def clean_url(self, url: str) -> str:
        if "#" in url:
            url = url.split("#")[0]
        return url

    async def track(self, url: str) -> Tuple[Union[dict, None], Union[str, None]]:
        try:
            details = await self.info(url)
            track_details = {
                "title": details.get("title", "JioSaavn Track"),
                "link": details.get("url", url),
                "vidid": details.get("_id", "saavn_track"),
                "duration_min": details.get("duration_min", "00:00"),
                "duration_sec": details.get("duration_sec", 0),
                "thumb": details.get("thumb", ""),
            }
            return track_details, details.get("_id", "saavn_track")
        except Exception:
            return None, None

    @asyncify
    def playlist(self, url, limit):
        clean_url = self.clean_url(url)
        ydl_opts = {
            "extract_flat": True,
            "force_generic_extractor": True,
            "quiet": True,
            "no_warnings": True,
        }
        song_info = []
        count = 0
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                playlist_info = ydl.extract_info(clean_url, download=False)
                for entry in playlist_info.get("entries", []):
                    if count == limit:
                        break
                    duration_sec = entry.get("duration", 0)
                    info = {
                        "title": entry.get("title", "JioSaavn Song"),
                        "duration_sec": duration_sec,
                        "duration_min": seconds_to_time(duration_sec),
                        "thumb": entry.get("thumbnail", ""),
                        "url": self.clean_url(entry.get("webpage_url", "")),
                    }
                    song_info.append(info)
                    count += 1
            except Exception:
                pass
        return song_info

    async def info(self, url):
        url = self.clean_url(url)

        async with aiohttp.ClientSession() as session:
            if "jiosaavn.com" in url:
                api_url = "https://saavn.dev/api/songs"
                params = {"link": url, "limit": 1}
            else:
                api_url = "https://saavn.dev/api/search/songs"
                params = {"query": url, "limit": 1}

            async with session.get(api_url, params=params, timeout=10) as response:
                data = await response.json()

                if "jiosaavn.com" in url:
                    info = data["data"][0]
                else:
                    info = data["data"]["results"][0]

                thumb_url = info["image"][-1]["url"]
                thumb_path = await self._resize_thumb(thumb_url, info["id"])

                return {
                    "title": info["name"],
                    "duration_sec": info.get("duration", 0),
                    "duration_min": seconds_to_time(info.get("duration", 0)),
                    "thumb": thumb_path,
                    "url": self.clean_url(info["url"]),
                    "_download_url": info["downloadUrl"][-1]["url"],
                    "_id": info["id"],
                }

    async def download(self, url):
        details = await self.info(url)
        os.makedirs("downloads", exist_ok=True)
        file_path = os.path.join("downloads", f"Saavn_{details['_id']}.mp3")

        if not os.path.exists(file_path):
            async with aiohttp.ClientSession() as session:
                async with session.get(details["_download_url"], timeout=30) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            while chunk := await resp.content.read(1024):
                                f.write(chunk)
                    else:
                        raise ValueError(
                            f"Failed to download {details['_download_url']}. HTTP Status: {resp.status}"
                        )

        details["filepath"] = file_path
        return file_path, details

    async def _resize_thumb(self, thumb_url, _id, size=(1280, 720)):
        os.makedirs("cache", exist_ok=True)
        thumb_path = os.path.join("cache", f"Thumb_{_id}.jpg")

        if os.path.exists(thumb_path):
            return thumb_path

        if Image is None:
            return thumb_url

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumb_url, timeout=10) as response:
                    img_data = await response.read()

            img = Image.open(BytesIO(img_data))
            scale_factor = size[1] / img.height
            new_width = int(img.width * scale_factor)
            new_height = size[1]

            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            new_img = Image.new("RGB", size, (0, 0, 0))
            new_img.paste(resized_img, ((size[0] - new_width) // 2, 0))

            new_img.save(thumb_path, format="JPEG")
            return thumb_path
        except Exception:
            return thumb_url
