# All rights reserved.
import re
import sys
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


# Get it from my.telegram.org
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")

## Get it from @Botfather in Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "")

# Database to save your chats and stats... 
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

CLEANMODE_DELETE_MINS = int(
    getenv("CLEANMODE_MINS", "5")
)  # Value in Seconds

# Custom max audio(music) duration for voice chat. Default 60 mins.
DURATION_LIMIT_MIN = int(
    getenv("DURATION_LIMIT", "5400")
)  # Value in Minutes

# Proxy URL for YouTube/yt-dlp requests (leave empty to disable)
PROXY_URL = getenv("PROXY_URL", "")

# Duration Limit for downloading Songs in MP3 or MP4 format from bot
SONG_DOWNLOAD_DURATION = int(
    getenv("SONG_DOWNLOAD_DURATION_LIMIT", "5400")
)  # Value in Minutes

# You'll need a Private Group ID for this.
LOGGER_ID = int(getenv("LOGGER_ID", ""))

# Your User ID.
OWNER_ID = list(
    map(int, getenv("OWNER_ID", "7048354045").split())
)

PRIVACY_LINK = getenv(
    "PRIVACY_LINK", "https://telegra.ph"
)

EXTRA_PLUGINS = getenv(
    "EXTRA_PLUGINS",
    "False",
)
EXTRA_PLUGINS_REPO = getenv(
    "EXTRA_PLUGINS_REPO",
    "",
)
EXTRA_PLUGINS_FOLDER = getenv("EXTRA_PLUGINS_FOLDER", "plugins")

AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", False)
AUTO_LEAVE_ASSISTANT_TIME = int(
    getenv("ASSISTANT_LEAVE_TIME", 5800)
)

# For customized or modified Repository
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Katsuki6608/Fubuki-Music-Bot",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "")  

PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", "False")
INSTANT_PLAY = getenv("INSTANT_PLAY", "True")

YOUTUBE_DOWNLOAD_EDIT_SLEEP = int(getenv("YOUTUBE_EDIT_SLEEP", "3"))
TELEGRAM_DOWNLOAD_EDIT_SLEEP = int(getenv("TELEGRAM_EDIT_SLEEP", "5"))

GITHUB_REPO = getenv("GITHUB_REPO", "https://github.com/Katsuki6608/Fubuki-Music-Bot")

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "")

VIDEO_STREAM_LIMIT = int(getenv("VIDEO_STREAM_LIMIT", "999"))
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "235"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "255"))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "1073741824"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824"))

SET_CMDS = getenv("SET_CMDS", "True")

raw_sessions = getenv("STRING_SESSIONS", "")
STRING_SESSIONS = list(map(str.strip, raw_sessions.split(","))) if raw_sessions else []

### DONT TOUCH or EDIT codes after this line
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

# Images
START_IMG_URL = getenv("START_IMG_URL", "https://te.legra.ph/file/7d9c0fec898bbee09ba95.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://te.legra.ph/file/95fcd2ec79b527ae3fac4.jpg")
PLAYLIST_IMG_URL = getenv("PLAYLIST_IMG_URL", "https://te.legra.ph/file/f739e6067725fa88ce8d3.jpg")
GLOBAL_IMG_URL = getenv("GLOBAL_IMG_URL", "https://te.legra.ph/file/95fcd2ec79b527ae3fac4.jpg")
STATS_IMG_URL = getenv("STATS_IMG_URL", "https://te.legra.ph/file/c66abbf490158487fdb72.jpg")
TELEGRAM_AUDIO_URL = getenv("TELEGRAM_AUDIO_URL", "https://te.legra.ph/file/3d130381bf5945c139023.jpg")
TELEGRAM_VIDEO_URL = getenv("TELEGRAM_VIDEO_URL", "https://te.legra.ph/file/d3663021fb51e14a84aa9.jpg")
STREAM_IMG_URL = getenv("STREAM_IMG_URL", "https://te.legra.ph/file/248e6858de3f2e37393c1.jpg")
SOUNCLOUD_IMG_URL = getenv("SOUNCLOUD_IMG_URL", "https://te.legra.ph/file/1b78431fe8de0e497c188.jpg")
YOUTUBE_IMG_URL = getenv("YOUTUBE_IMG_URL", "https://te.legra.ph/file/98622051acad1988886be.jpg")
SPOTIFY_ARTIST_IMG_URL = getenv("SPOTIFY_ARTIST_IMG_URL", "https://te.legra.ph/file/c03f25028fa248401d519.jpg")
SPOTIFY_ALBUM_IMG_URL = getenv("SPOTIFY_ALBUM_IMG_URL", "https://te.legra.ph/file/9fe24bde84b1d31f685a9.jpg")
SPOTIFY_PLAYLIST_IMG_URL = getenv("SPOTIFY_PLAYLIST_IMG_URL", "https://te.legra.ph/file/7345db59ab5d2c5cb142a.jpg")


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


def seconds_to_time(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SONG_DOWNLOAD_DURATION_LIMIT = int(time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        print("[ERROR] - Your SUPPORT_CHANNEL url is wrong.")
        sys.exit()

if SUPPORT_GROUP:
    if not re.match("(?:http|https)://", SUPPORT_GROUP):
        print("[ERROR] - Your SUPPORT_GROUP url is wrong.")
        sys.exit()

if UPSTREAM_REPO:
    if not re.match("(?:http|https)://", UPSTREAM_REPO):
        print("[ERROR] - Your UPSTREAM_REPO url is wrong.")
        sys.exit()

if GITHUB_REPO:
    if not re.match("(?:http|https)://", GITHUB_REPO):
        print("[ERROR] - Your GITHUB_REPO url is wrong.")
        sys.exit()
