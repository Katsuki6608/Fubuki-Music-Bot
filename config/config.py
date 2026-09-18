# All rights reserved.
import re
import sys
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


# Helper function for safe integer parsing
def get_int(var_name: str, default: int = 0) -> int:
    val = getenv(var_name, "").strip()
    try:
        return int(val) if val else default
    except ValueError:
        return default


# Telegram API Credentials (my.telegram.org)
API_ID = get_int("API_ID", 0)
API_HASH = getenv("API_HASH", "").strip()

# Bot Token (@BotFather)
BOT_TOKEN = getenv("BOT_TOKEN", "").strip()

# Database
MONGO_DB_URI = getenv("MONGO_DB_URI", "").strip()

# Cleanup and Duration Limits
CLEANMODE_DELETE_MINS = get_int("CLEANMODE_MINS", 5)
DURATION_LIMIT_MIN = get_int("DURATION_LIMIT", 5400)
SONG_DOWNLOAD_DURATION = get_int("SONG_DOWNLOAD_DURATION_LIMIT", 5400)

# Proxy Configuration
PROXY_URL = getenv("PROXY_URL", "").strip()

# Logger Group ID (e.g. -100xxxxxxxxxx)
LOGGER_ID = get_int("LOGGER_ID", 0)

# Owner IDs (Accepts space or comma-separated user IDs)
raw_owner = getenv("OWNER_ID", "7048354045").replace(",", " ")
OWNER_ID = [int(x) for x in raw_owner.split() if x.isdigit()]
if not OWNER_ID:
    OWNER_ID = [7048354045]

PRIVACY_LINK = getenv("PRIVACY_LINK", "https://telegra.ph").strip()

EXTRA_PLUGINS = getenv("EXTRA_PLUGINS", "False").strip()
EXTRA_PLUGINS_REPO = getenv("EXTRA_PLUGINS_REPO", "").strip()
EXTRA_PLUGINS_FOLDER = getenv("EXTRA_PLUGINS_FOLDER", "plugins").strip()

AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False").strip()
AUTO_LEAVE_ASSISTANT_TIME = get_int("ASSISTANT_LEAVE_TIME", 5800)

# Git & Upstream
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Katsuki6608/Fubuki-Music-Bot",
).strip()
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main").strip()
GIT_TOKEN = getenv("GIT_TOKEN", "").strip()

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "").strip()
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "").strip()

PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", "False").strip()
INSTANT_PLAY = getenv("INSTANT_PLAY", "True").strip()

YOUTUBE_DOWNLOAD_EDIT_SLEEP = get_int("YOUTUBE_EDIT_SLEEP", 3)
TELEGRAM_DOWNLOAD_EDIT_SLEEP = get_int("TELEGRAM_EDIT_SLEEP", 5)

GITHUB_REPO = getenv(
    "GITHUB_REPO",
    "https://github.com/Katsuki6608/Fubuki-Music-Bot",
).strip()

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "").strip()
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "").strip()

VIDEO_STREAM_LIMIT = get_int("VIDEO_STREAM_LIMIT", 999)
SERVER_PLAYLIST_LIMIT = get_int("SERVER_PLAYLIST_LIMIT", 235)
PLAYLIST_FETCH_LIMIT = get_int("PLAYLIST_FETCH_LIMIT", 255)

TG_AUDIO_FILESIZE_LIMIT = get_int("TG_AUDIO_FILESIZE_LIMIT", 1073741824)
TG_VIDEO_FILESIZE_LIMIT = get_int("TG_VIDEO_FILESIZE_LIMIT", 1073741824)

SET_CMDS = getenv("SET_CMDS", "True").strip()

# String Sessions for Assistant
raw_sessions = getenv("STRING_SESSIONS", "")
STRING_SESSIONS = (
    [s.strip() for s in raw_sessions.split(",") if s.strip()]
    if raw_sessions
    else []
)

### System Globals
BANNED_USERS = filters.user()
YTDOWNLOADER = 1
LOG = 2
LOG_FILE_NAME = "FubukiLog.txt"
TEMP_DB_FOLDER = "tempdb"
adminlist = {}
lyrical = {}
chatstats = {}
userstats = {}
clean = {}
autoclean = []

# Asset URLs
START_IMG_URL = getenv("START_IMG_URL", "https://telegra.ph/file/7d9c0fec898bbee09ba95.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/95fcd2ec79b527ae3fac4.jpg")
PLAYLIST_IMG_URL = getenv("PLAYLIST_IMG_URL", "https://telegra.ph/file/f739e6067725fa88ce8d3.jpg")
GLOBAL_IMG_URL = getenv("GLOBAL_IMG_URL", "https://telegra.ph/file/95fcd2ec79b527ae3fac4.jpg")
STATS_IMG_URL = getenv("STATS_IMG_URL", "https://telegra.ph/file/c66abbf490158487fdb72.jpg")
TELEGRAM_AUDIO_URL = getenv("TELEGRAM_AUDIO_URL", "https://telegra.ph/file/3d130381bf5945c139023.jpg")
TELEGRAM_VIDEO_URL = getenv("TELEGRAM_VIDEO_URL", "https://telegra.ph/file/d3663021fb51e14a84aa9.jpg")
STREAM_IMG_URL = getenv("STREAM_IMG_URL", "https://telegra.ph/file/248e6858de3f2e37393c1.jpg")
SOUNCLOUD_IMG_URL = getenv("SOUNCLOUD_IMG_URL", "https://telegra.ph/file/1b78431fe8de0e497c188.jpg")
YOUTUBE_IMG_URL = getenv("YOUTUBE_IMG_URL", "https://telegra.ph/file/98622051acad1988886be.jpg")
SPOTIFY_ARTIST_IMG_URL = getenv("SPOTIFY_ARTIST_IMG_URL", "https://telegra.ph/file/c03f25028fa248401d519.jpg")
SPOTIFY_ALBUM_IMG_URL = getenv("SPOTIFY_ALBUM_IMG_URL", "https://telegra.ph/file/9fe24bde84b1d31f685a9.jpg")
SPOTIFY_PLAYLIST_IMG_URL = getenv("SPOTIFY_PLAYLIST_IMG_URL", "https://telegra.ph/file/7345db59ab5d2c5cb142a.jpg")


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


def seconds_to_time(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SONG_DOWNLOAD_DURATION_LIMIT = int(time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00"))

# Validation
if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    print("[ERROR] - Your SUPPORT_CHANNEL url is invalid.")
    sys.exit()

if SUPPORT_GROUP and not re.match(r"(?:http|https)://", SUPPORT_GROUP):
    print("[ERROR] - Your SUPPORT_GROUP url is invalid.")
    sys.exit()

if UPSTREAM_REPO and not re.match(r"(?:http|https)://", UPSTREAM_REPO):
    print("[ERROR] - Your UPSTREAM_REPO url is invalid.")
    sys.exit()

if GITHUB_REPO and not re.match(r"(?:http|https)://", GITHUB_REPO):
    print("[ERROR] - Your GITHUB_REPO url is invalid.")
    sys.exit()
