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

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class Apple:
    def __init__(self):
        self.regex = r"^(https:\/\/music\.apple\.com\/)(.*)$"
        self.base = "https://music.apple.com/in/playlist/"

    async def valid(self, link: str) -> bool:
        if re.search(self.regex, link):
            return True
        return False

    async def track(self, url: str, playid: Union[bool, str] = None) -> Tuple[Union[dict, None], Union[str, None]]:
        if playid:
            url = self.base + str(url)
        try:
            async with aiohttp.ClientSession(headers=_HEADERS) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return None, None
                    html = await response.text()
        except Exception:
            return None, None

        soup = BeautifulSoup(html, "html.parser")
        search = None
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:title":
                search = tag.get("content")
                break

        if not search:
            return None, None

        try:
            if VideosSearch is not None:
                results = VideosSearch(search, limit=1)
                search_result = await results.next()
                items = search_result.get("result", [])
                if items:
                    result = items[0]
                    track_details = {
                        "title": result.get("title", "Apple Music Track"),
                        "link": result.get("link", ""),
                        "vidid": result.get("id", ""),
                        "duration_min": result.get("duration", "00:00"),
                        "thumb": result["thumbnails"][0]["url"].split("?")[0] if result.get("thumbnails") else "",
                    }
                    return track_details, track_details["vidid"]

            from yt_dlp import YoutubeDL
            with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{search}", download=False)
                if info_dict and "entries" in info_dict and info_dict["entries"]:
                    entry = info_dict["entries"][0]
                    track_details = {
                        "title": entry.get("title", "Apple Music Track"),
                        "link": entry.get("webpage_url") or entry.get("url", ""),
                        "vidid": entry.get("id", ""),
                        "duration_min": "00:00",
                        "thumb": entry.get("thumbnail", ""),
                    }
                    return track_details, track_details["vidid"]
        except Exception:
            pass

        return None, None

    async def playlist(self, url: str, playid: Union[bool, str] = None) -> Tuple[list, Union[str, None]]:
        if playid:
            url = self.base + str(url)
        try:
            playlist_id = url.split("playlist/")[1].split("?")[0]
        except Exception:
            playlist_id = "apple_playlist"

        try:
            async with aiohttp.ClientSession(headers=_HEADERS) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return [], playlist_id
                    html = await response.text()
        except Exception:
            return [], playlist_id

        soup = BeautifulSoup(html, "html.parser")
        applelinks = soup.find_all("meta", attrs={"property": "music:song"})
        results = []
        for item in applelinks:
            try:
                content = item.get("content", "")
                if "album/" in content:
                    raw = (content.split("album/")[1]).split("/")[0]
                    xx = raw.replace("-", " ")
                    results.append(xx)
            except Exception:
                continue
        return results, playlist_id
