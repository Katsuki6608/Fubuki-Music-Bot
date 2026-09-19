# All rights reserved.
#

import re
from typing import Tuple, Union

import aiohttp
from bs4 import BeautifulSoup

try:
    from py_yt import VideosSearch
except ImportError:
    try:
        from youtubesearchpython import VideosSearch
    except ImportError:
        VideosSearch = None


class Resso:
    def __init__(self):
        self.regex = r"^(https:\/\/m\.resso\.com\/)(.*)$"
        self.base = "https://m.resso.com/"

    async def valid(self, link: str) -> bool:
        if re.search(self.regex, link):
            return True
        return False

    async def track(self, url: str, playid: Union[bool, str] = None) -> Tuple[Union[dict, None], Union[str, None]]:
        if playid:
            url = self.base + url
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return None, None
                    html = await response.text()
        except Exception:
            return None, None

        soup = BeautifulSoup(html, "html.parser")
        title = None
        des = None
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:title":
                title = tag.get("content")
            if tag.get("property") == "og:description":
                des = tag.get("content")
                try:
                    des = des.split("·")[0]
                except Exception:
                    pass

        search_query = title or des
        if not search_query:
            return None, None

        query_full = f"{search_query} {des}" if des and des != search_query else search_query

        try:
            if VideosSearch is not None:
                results = VideosSearch(query_full, limit=1)
                search_result = await results.next()
                items = search_result.get("result", [])
                if items:
                    result = items[0]
                    track_details = {
                        "title": result.get("title", "Resso Track"),
                        "link": result.get("link", ""),
                        "vidid": result.get("id", ""),
                        "duration_min": result.get("duration", "00:00"),
                        "thumb": result["thumbnails"][0]["url"].split("?")[0] if result.get("thumbnails") else "",
                    }
                    return track_details, track_details["vidid"]

            from yt_dlp import YoutubeDL
            with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{query_full}", download=False)
                if info_dict and "entries" in info_dict and info_dict["entries"]:
                    entry = info_dict["entries"][0]
                    track_details = {
                        "title": entry.get("title", "Resso Track"),
                        "link": entry.get("webpage_url") or entry.get("url", ""),
                        "vidid": entry.get("id", ""),
                        "duration_min": "00:00",
                        "thumb": entry.get("thumbnail", ""),
                    }
                    return track_details, track_details["vidid"]
        except Exception:
            pass

        return None, None
