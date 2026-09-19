# All rights reserved.
#

import asyncio
import re
from typing import Tuple, Union

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    spotipy = None
    SpotifyClientCredentials = None

try:
    from py_yt import VideosSearch
except ImportError:
    try:
        from youtubesearchpython import VideosSearch
    except ImportError:
        VideosSearch = None

import config

try:
    from Fubuki.utils.decorators import asyncify
except Exception:
    def asyncify(func):
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper


class Spotify:
    def __init__(self):
        self.regex = r"^(https:\/\/open.spotify.com\/)(.*)$"
        self.client_id = getattr(config, "SPOTIFY_CLIENT_ID", None)
        self.client_secret = getattr(config, "SPOTIFY_CLIENT_SECRET", None)

        if spotipy and self.client_id and self.client_secret:
            try:
                self.client_credentials_manager = SpotifyClientCredentials(
                    self.client_id, self.client_secret
                )
                self.spotify = spotipy.Spotify(
                    client_credentials_manager=self.client_credentials_manager
                )
            except Exception:
                self.spotify = None
        else:
            self.spotify = None

    async def valid(self, link: str):
        if re.search(self.regex, link):
            return True
        return False

    async def track(self, link: str):
        if not self.spotify:
            return None, None

        try:
            track_info = self.spotify.track(link)
            info = track_info["name"]
            for artist in track_info.get("artists", []):
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched

            if VideosSearch is not None:
                results = VideosSearch(info, limit=1)
                search_result = await results.next()
                items = search_result.get("result", [])
                if items:
                    result = items[0]
                    track_details = {
                        "title": result.get("title", "Audio Track"),
                        "link": result.get("link", ""),
                        "vidid": result.get("id", ""),
                        "duration_min": result.get("duration", "00:00"),
                        "thumb": result["thumbnails"][0]["url"].split("?")[0] if result.get("thumbnails") else "",
                    }
                    return track_details, track_details["vidid"]

            from yt_dlp import YoutubeDL
            ydl_opts = {"quiet": True, "no_warnings": True}
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{info}", download=False)
                if info_dict and "entries" in info_dict and info_dict["entries"]:
                    entry = info_dict["entries"][0]
                    track_details = {
                        "title": entry.get("title", "Audio Track"),
                        "link": entry.get("webpage_url") or entry.get("url", ""),
                        "vidid": entry.get("id", ""),
                        "duration_min": "00:00",
                        "thumb": entry.get("thumbnail", ""),
                    }
                    return track_details, track_details["vidid"]

        except Exception:
            pass

        return None, None

    @asyncify
    def playlist(self, url: str) -> Tuple[list, Union[str, None]]:
        if not self.spotify:
            return [], None
        try:
            playlist_data = self.spotify.playlist(url)
            playlist_id = playlist_data["id"]
            results = []
            for item in playlist_data.get("tracks", {}).get("items", []):
                music_track = item.get("track")
                if not music_track:
                    continue
                info = music_track["name"]
                for artist in music_track.get("artists", []):
                    fetched = f' {artist["name"]}'
                    if "Various Artists" not in fetched:
                        info += fetched
                results.append(info)
            return results, playlist_id
        except Exception:
            return [], None

    @asyncify
    def album(self, url: str) -> Tuple[list, Union[str, None]]:
        if not self.spotify:
            return [], None
        try:
            album_data = self.spotify.album(url)
            album_id = album_data["id"]
            results = []
            for item in album_data.get("tracks", {}).get("items", []):
                info = item["name"]
                for artist in item.get("artists", []):
                    fetched = f' {artist["name"]}'
                    if "Various Artists" not in fetched:
                        info += fetched
                results.append(info)
            return results, album_id
        except Exception:
            return [], None

    @asyncify
    def artist(self, url: str) -> Tuple[list, Union[str, None]]:
        if not self.spotify:
            return [], None
        try:
            artist_info = self.spotify.artist(url)
            artist_id = artist_info["id"]
            results = []
            artist_top_tracks = self.spotify.artist_top_tracks(url)
            for item in artist_top_tracks.get("tracks", []):
                info = item["name"]
                for artist in item.get("artists", []):
                    fetched = f' {artist["name"]}'
                    if "Various Artists" not in fetched:
                        info += fetched
                results.append(info)
            return results, artist_id
        except Exception:
            return [], None
