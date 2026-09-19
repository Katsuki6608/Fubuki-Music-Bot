# All rights reserved.
#
import asyncio
import os
import re
import shlex
import shutil
import time
from typing import Union

import httpx

try:
    from async_lru import alru_cache
except ImportError:
    def alru_cache(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

try:
    from py_yt import VideosSearch
except ImportError:
    try:
        from youtubesearchpython import VideosSearch
    except ImportError:
        VideosSearch = None

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from yt_dlp import YoutubeDL

try:
    from Fubuki.utils.decorators import asyncify
except Exception:
    def asyncify(func):
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper

try:
    from Fubuki.utils.formatters import seconds_to_min, time_to_seconds
except Exception:
    def seconds_to_min(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    def time_to_seconds(time_str):
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(str(time_str).split(":"))))

async def notify_owner(*args, **kwargs):
    pass

_LOG_TAG = "Youtube"
_YT_SEARCH_TIMEOUT = 10
_YT_DLP_TIMEOUT = 60
_YT_SUBPROCESS_TIMEOUT = 60
_YT_STREAM_CHECK_TIMEOUT = 8


def _log(level, msg, *a, **kw):
    import logging
    logger = logging.getLogger("Fubuki.platforms.Youtube")
    if hasattr(logger, level):
        getattr(logger, level)(f"[{_LOG_TAG}] {msg}", *a, **kw)


def yt_dlp_binary():
    path = shutil.which("yt-dlp")
    if path:
        return path
    for candidate in (
        os.path.expanduser("~/.local/bin/yt-dlp"),
        os.path.expanduser("~/bin/yt-dlp"),
        "/usr/local/bin/yt-dlp",
        "/usr/bin/yt-dlp",
        "/usr/sbin/yt-dlp",
    ):
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return "yt-dlp"


def cookies():
    folder_path = f"{os.getcwd()}/cookies"
    if not os.path.isdir(folder_path):
        return None
    txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]
    if not txt_files:
        return None
    for cookie_txt_file in txt_files:
        cookie_txt_file = os.path.join(folder_path, cookie_txt_file)
        try:
            with open(cookie_txt_file) as f:
                header = f.read(200)
        except Exception:
            continue
        if "# Netscape HTTP Cookie File" in header or "# HTTP Cookie File" in header:
            return cookie_txt_file
    return None


try:
    from config import PROXY_URL
    PROXY = PROXY_URL if PROXY_URL else None
except Exception:
    PROXY = None

RUNTIME_PRIORITY = ["node", "bun", "deno"]

_YT_CLIENTS = ["tv", "mweb", "web"]
_YT_CLIENTS_STR = "tv,mweb,web"
_AUDIO_FMT = "bestaudio/best/18/worst"
_VIDEO_FMT = (
    "bestvideo[height<=?2160][ext=mp4]+bestaudio[ext=m4a]/"
    "bestvideo[height<=?2160]+bestaudio/"
    "best[height<=?2160]/18/best"
)


def _find_browser():
    env = os.getenv("WPC_BROWSER_PATH", "").strip()
    if env and os.path.isfile(env):
        return env
    for name in ("chromium-browser", "chromium", "google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    import glob as _glob
    for pattern in (
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        "/usr/lib/chromium/chrome",
        "/opt/google/chrome/chrome",
    ):
        matches = sorted(_glob.glob(pattern))
        if matches:
            return matches[-1]
    return ""


_WPC_BROWSER_PATH = _find_browser()
_WPC_BROWSER_ARGS = {"no_sandbox": True}
_POT_PROVIDERS = ["wpc"]


def _wpc_extractor_args():
    if not _WPC_BROWSER_PATH:
        return None
    return {"browser_path": _WPC_BROWSER_PATH, **_WPC_BROWSER_ARGS}


def _pot_args():
    if not _WPC_BROWSER_PATH:
        return []
    args = []
    for provider in _POT_PROVIDERS:
        args.extend(["--extractor-args", f"youtubepot-wpc:browser_path={_WPC_BROWSER_PATH}"])
        for key, val in _WPC_BROWSER_ARGS.items():
            args.extend(["--extractor-args", f"youtubepot-wpc:{key}={val}"])
    return args


def _proxy_args():
    if not PROXY:
        return []
    return ["--proxy", PROXY]


def _proxy_dict():
    if not PROXY:
        return {}
    return {"proxy": PROXY}


def _cookie_args():
    path = cookies()
    if not path:
        return []
    return ["--cookies", path]


def _cookie_dict():
    path = cookies()
    if not path:
        return {}
    return {"cookiefile": path}


def _aria2_proxy_args():
    if not PROXY:
        return []
    return [f"--all-proxy={PROXY}"]


_YT_HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _base_ydl_opts(**extra):
    extractor_args = {"youtube": {"player_client": list(_YT_CLIENTS)}}
    wpc = _wpc_extractor_args()
    if wpc:
        extractor_args["youtubepot-wpc"] = wpc
    opts = {
        "extractor_args": extractor_args,
        **_proxy_dict(),
        **_cookie_dict(),
        "geo_bypass": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "prefer_ffmpeg": True,
        "no_overwrites": True,
        "remote_components": ["ejs:github"],
        "extractor_retries": 5,
        "fragment_retries": 5,
        "retries": 5,
        "concurrent_fragment_downloads": 5,
        "buffersize": "1024K",
        "http_chunk_size": "10M",
        "http_headers": _YT_HTTP_HEADERS,
        "postprocessor_args": {
            "ffmpeg": ["-threads", "4", "-preset", "slow", "-q:a", "0"],
        },
    }
    if shutil.which("aria2c"):
        opts["external_downloader"] = "aria2c"
        opts["external_downloader_args"] = [
            "-x", "16", "-s", "16", "-k", "1M",
            *_aria2_proxy_args(),
        ]
    opts.update(extra)
    return opts


def get_available_runtimes():
    return [rt for rt in RUNTIME_PRIORITY if shutil.which(rt)]


def extract_info_with_fallback(link, opts):
    runtimes = get_available_runtimes() or [None]
    last_error = None
    attempts = []
    for runtime in runtimes:
        temp_opts = opts.copy()
        if runtime:
            temp_opts["js_runtime"] = runtime
        attempts.append((runtime or "default", temp_opts))
    fallback_opts = opts.copy()
    fallback_opts["format"] = "18/best/worst"
    if runtimes and runtimes[0]:
        fallback_opts["js_runtime"] = runtimes[0]
    attempts.append(("progressive-18", fallback_opts))

    for label, temp_opts in attempts:
        try:
            with YoutubeDL(temp_opts) as ydl:
                return ydl.extract_info(link)
        except Exception as e:
            last_error = e
            continue
    raise Exception(f"All extract attempts failed: {last_error}")


NOTHING = {"cookies_dead": None}


async def shell_cmd(cmd):
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, errorz = await asyncio.wait_for(
            proc.communicate(), timeout=_YT_SUBPROCESS_TIMEOUT
        )
        if errorz:
            if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
                return out.decode("utf-8")
            else:
                return errorz.decode("utf-8")
        return out.decode("utf-8")
    except Exception:
        return ""


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    @property
    def use_fallback(self):
        return NOTHING["cookies_dead"] is True

    @use_fallback.setter
    def use_fallback(self, value):
        if NOTHING["cookies_dead"] is None:
            NOTHING["cookies_dead"] = value

    async def url(self, *args, **kwargs) -> Union[str, None]:
        if not args:
            return None
        messages = []
        for a in args:
            if isinstance(a, Message):
                messages.append(a)
                if a.reply_to_message:
                    messages.append(a.reply_to_message)
            elif isinstance(a, str):
                return a.strip()

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption or ""
                        return text[entity.offset : entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        for message in messages:
            text = message.text or message.caption or ""
            parts = text.split(None, 1)
            if len(parts) > 1:
                return parts[1].strip()

        return None

    @alru_cache(maxsize=256)
    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            if VideosSearch is not None:
                results = VideosSearch(link, limit=1, timeout=_YT_SEARCH_TIMEOUT)
                search_result = await asyncio.wait_for(
                    results.next(), timeout=_YT_SEARCH_TIMEOUT + 5
                )
                items = search_result.get("result", [])
                if items:
                    result = items[0]
                    title = result["title"]
                    duration_min = result["duration"]
                    thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                    vidid = result["id"]
                    duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
                    return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            pass

        info, vidid = await self._track(link)
        return info["title"], info["duration_min"], 0, info["thumb"], vidid

    @alru_cache(maxsize=256)
    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            if VideosSearch is not None:
                results = VideosSearch(link, limit=1, timeout=_YT_SEARCH_TIMEOUT)
                search_result = await asyncio.wait_for(
                    results.next(), timeout=_YT_SEARCH_TIMEOUT + 5
                )
                items = search_result.get("result", [])
                if items:
                    return items[0]["title"]
        except Exception:
            pass
        info, _ = await self._track(link)
        return info.get("title", "Audio Stream")

    @alru_cache(maxsize=256)
    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            if VideosSearch is not None:
                results = VideosSearch(link, limit=1, timeout=_YT_SEARCH_TIMEOUT)
                search_result = await asyncio.wait_for(
                    results.next(), timeout=_YT_SEARCH_TIMEOUT + 5
                )
                items = search_result.get("result", [])
                if items:
                    return items[0]["duration"]
        except Exception:
            pass
        info, _ = await self._track(link)
        return info.get("duration_min", "00:00")

    @alru_cache(maxsize=256)
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            if VideosSearch is not None:
                results = VideosSearch(link, limit=1, timeout=_YT_SEARCH_TIMEOUT)
                search_result = await asyncio.wait_for(
                    results.next(), timeout=_YT_SEARCH_TIMEOUT + 5
                )
                items = search_result.get("result", [])
                if items:
                    return items[0]["thumbnails"][0]["url"].split("?")[0]
        except Exception:
            pass
        info, _ = await self._track(link)
        return info.get("thumb", "")

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        cmd = [
            yt_dlp_binary(),
            *_proxy_args(),
            *_cookie_args(),
            "-g",
            "-f",
            _VIDEO_FMT,
            "--extractor-args", f"youtube:player_client={_YT_CLIENTS_STR}",
            *_pot_args(),
            "--remote-components", "ejs:github",
            f"{link}",
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=_YT_SUBPROCESS_TIMEOUT
            )
            if stdout:
                url = stdout.decode().split("\n")[0]
                return 1, url
            else:
                return 0, stderr.decode()[:200]
        except Exception as e:
            return 0, str(e)

    async def _streamable(self, url: str) -> bool:
        try:
            proxies = PROXY if PROXY else None
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=_YT_STREAM_CHECK_TIMEOUT,
                proxy=proxies,
                headers=_YT_HTTP_HEADERS,
            ) as client:
                resp = await client.get(url, headers={"Range": "bytes=0-1023"})
            return resp.status_code in (200, 206)
        except Exception:
            return True

    async def stream_url(
        self,
        link: str,
        videoid: Union[bool, str] = None,
        video: bool = False,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        fmt = _VIDEO_FMT if video else _AUDIO_FMT
        cmd = [
            yt_dlp_binary(),
            *_proxy_args(),
            *_cookie_args(),
            "-g",
            "-f",
            fmt,
            "--no-playlist",
            "--extractor-args", f"youtube:player_client={_YT_CLIENTS_STR}",
            *_pot_args(),
            "--remote-components", "ejs:github",
            "--user-agent", _YT_HTTP_HEADERS["User-Agent"],
            f"{link}",
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=_YT_SUBPROCESS_TIMEOUT
            )
            if stdout:
                lines = [ln.strip() for ln in stdout.decode().splitlines() if ln.strip()]
                url = next((ln for ln in lines if ln.startswith("http")), lines[0] if lines else "")
                if not url:
                    return 0, "empty url"
                return 1, url
            else:
                return 0, stderr.decode()[:200]
        except Exception as e:
            return 0, str(e)

    @alru_cache(maxsize=256)
    async def playlist(self, link, limit, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        proxy_part = f"--proxy {shlex.quote(PROXY)} " if PROXY else ""
        cookie_path = cookies()
        cookie_part = f"--cookies {shlex.quote(cookie_path)} " if cookie_path else ""
        pot_part = f"--extractor-args 'youtubepot-wpc:browser_path={_WPC_BROWSER_PATH}' " if _WPC_BROWSER_PATH else ""
        cmd = (
            f"{shlex.quote(yt_dlp_binary())} {proxy_part}{cookie_part}{pot_part}"
            f"-i --compat-options no-youtube-unavailable-videos "
            f"--extractor-args 'youtube:player_client={_YT_CLIENTS_STR}' "
            f'--get-id --flat-playlist --playlist-end {limit} --skip-download "{link}" '
            f"2>/dev/null"
        )
        playlist_str = await shell_cmd(cmd)
        try:
            result = [key for key in playlist_str.split("\n") if key]
        except Exception:
            result = []
        return result

    @alru_cache(maxsize=256)
    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if link.startswith("http://") or link.startswith("https://"):
            return await self._track(link)
        try:
            if VideosSearch is not None:
                results = VideosSearch(link, limit=1, timeout=_YT_SEARCH_TIMEOUT)
                search_result = await asyncio.wait_for(
                    results.next(), timeout=_YT_SEARCH_TIMEOUT + 5
                )
                items = search_result.get("result", [])
                if items:
                    result = items[0]
                    title = result["title"]
                    duration_min = result["duration"]
                    vidid = result["id"]
                    yturl = result["link"]
                    thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                    track_details = {
                        "title": title,
                        "link": yturl,
                        "vidid": vidid,
                        "duration_min": duration_min,
                        "thumb": thumbnail,
                    }
                    return track_details, vidid
        except Exception:
            pass
        return await self._track(link)

    @asyncify
    def _track(self, q):
        extractor_args = {"youtube": {"player_client": list(_YT_CLIENTS)}}
        wpc = _wpc_extractor_args()
        if wpc:
            extractor_args["youtubepot-wpc"] = wpc
        options = {
            "format": _AUDIO_FMT,
            "noplaylist": True,
            "quiet": True,
            "extract_flat": "in_playlist",
            "extractor_args": extractor_args,
            **_proxy_dict(),
            **_cookie_dict(),
            "remote_components": ["ejs:github"],
        }
        with YoutubeDL(options) as ydl:
            query = q if (q.startswith("http://") or q.startswith("https://")) else f"ytsearch: {q}"
            info_dict = ydl.extract_info(query, download=False)
            if not info_dict:
                raise Exception("no entries from ytsearch")
            if "entries" in info_dict and info_dict["entries"]:
                details = info_dict["entries"][0]
            else:
                details = info_dict
            
            dur = details.get("duration")
            info = {
                "title": details.get("title", "Audio Track"),
                "link": details.get("webpage_url") or details.get("url") or q,
                "vidid": details.get("id", "track"),
                "duration_min": seconds_to_min(dur) if dur else None,
                "thumb": details.get("thumbnail") or (details.get("thumbnails")[0]["url"] if details.get("thumbnails") else ""),
            }
            return info, details.get("id", "track")

    @alru_cache(maxsize=256)
    @asyncify
    def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        ytdl_opts = {
            "quiet": True,
            "extractor_args": {"youtube": {"player_client": list(_YT_CLIENTS)}},
            **_proxy_dict(),
            **_cookie_dict(),
            "remote_components": ["ejs:github"],
            "extractor_retries": 5,
            "fragment_retries": 5,
            "retries": 5,
        }
        wpc = _wpc_extractor_args()
        if wpc:
            ytdl_opts["extractor_args"]["youtubepot-wpc"] = wpc

        ydl = YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for fmt in r.get("formats", []):
                if "dash" not in str(fmt.get("format", "")).lower():
                    try:
                        formats_available.append(
                            {
                                "format": fmt["format"],
                                "filesize": fmt.get("filesize"),
                                "format_id": fmt["format_id"],
                                "ext": fmt.get("ext"),
                                "format_note": fmt.get("format_note"),
                                "yturl": link,
                            }
                        )
                    except KeyError:
                        continue
        return formats_available, link

    @alru_cache(maxsize=256)
    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            if VideosSearch is not None:
                a = VideosSearch(link, limit=10, timeout=_YT_SEARCH_TIMEOUT)
                search_result = await asyncio.wait_for(
                    a.next(), timeout=_YT_SEARCH_TIMEOUT + 5
                )
                result = search_result.get("result")
                if result and len(result) > query_type:
                    title = result[query_type]["title"]
                    duration_min = result[query_type]["duration"]
                    vidid = result[query_type]["id"]
                    thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
                    return title, duration_min, thumbnail, vidid
        except Exception:
            pass
        return "Audio Stream", "00:00", "", ""

    async def download(
        self,
        link: str,
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> tuple:
        if videoid:
            link = self.base + link

        os.makedirs("downloads", exist_ok=True)

        @asyncify
        def audio_dl():
            ydl_optssx = _base_ydl_opts(
                format=_AUDIO_FMT,
                outtmpl="downloads/%(id)s.%(ext)s",
            )
            info = extract_info_with_fallback(link, ydl_optssx)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz) and os.path.getsize(xyz) >= 10240:
                return xyz
            with YoutubeDL(ydl_optssx) as x:
                x.download([link])
                return xyz

        @asyncify
        def video_dl():
            ydl_optssx = _base_ydl_opts(
                format=_VIDEO_FMT,
                outtmpl="downloads/%(id)s.%(ext)s",
                merge_output_format="mp4",
            )
            info = extract_info_with_fallback(link, ydl_optssx)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz) and os.path.getsize(xyz) >= 10240:
                return xyz
            with YoutubeDL(ydl_optssx) as x:
                x.download([link])
                return xyz

        @asyncify
        def song_video_dl():
            formats = f"{format_id}+bestaudio/best/18/best" if format_id else _VIDEO_FMT
            ydl_optssx = _base_ydl_opts(
                format=formats,
                outtmpl=os.path.join("downloads", f"%(id)s_{format_id}.%(ext)s"),
                merge_output_format="mp4",
            )
            info = extract_info_with_fallback(link, ydl_optssx)
            with YoutubeDL(ydl_optssx) as x:
                filename = f"{info['id']}_{format_id}.mp4"
                file_path = os.path.join("downloads", filename)
                return file_path

        @asyncify
        def song_audio_dl():
            ydl_optssx = _base_ydl_opts(
                format=format_id or _AUDIO_FMT,
                outtmpl=os.path.join("downloads", f"%(id)s_{format_id}.%(ext)s"),
                postprocessors=[
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                postprocessor_args={"ffmpeg": ["-threads", "4", "-b:a", "192k"]},
            )
            info = extract_info_with_fallback(link, ydl_optssx)
            with YoutubeDL(ydl_optssx) as x:
                filename = f"{info['id']}_{format_id}.mp3"
                file_path = os.path.join("downloads", filename)
                return file_path

        if songvideo:
            result = await asyncio.wait_for(song_video_dl(), timeout=_YT_DLP_TIMEOUT * 3)
        elif songaudio:
            result = await asyncio.wait_for(song_audio_dl(), timeout=_YT_DLP_TIMEOUT * 3)
        elif video:
            result = await asyncio.wait_for(video_dl(), timeout=_YT_DLP_TIMEOUT * 3)
        else:
            result = await asyncio.wait_for(audio_dl(), timeout=_YT_DLP_TIMEOUT * 3)

        return result, True
