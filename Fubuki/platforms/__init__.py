# All rights reserved.
#

# --- Apple Safe Import ---
try:
    from .Apple import Apple
except Exception:
    class Apple:
        def __init__(self):
            pass
        async def valid(self, *args, **kwargs):
            return False
        async def track(self, *args, **kwargs):
            return None, None
        async def playlist(self, *args, **kwargs):
            return []

# --- Carbon Safe Import ---
try:
    from .Carbon import Carbon
except Exception:
    class Carbon:
        def __init__(self):
            pass
        async def generate(self, *args, **kwargs):
            return None

# --- JioSaavn Safe Import ---
try:
    from .JioSavan import Saavn
except Exception:
    try:
        from .JioSaavn import Saavn
    except Exception:
        class Saavn:
            def __init__(self):
                pass
            async def valid(self, *args, **kwargs):
                return False
            async def track(self, *args, **kwargs):
                return None, None
            async def playlist(self, *args, **kwargs):
                return []

# --- Resso Safe Import ---
try:
    from .Resso import Resso
except Exception:
    class Resso:
        def __init__(self):
            pass
        async def valid(self, *args, **kwargs):
            return False
        async def track(self, *args, **kwargs):
            return None, None

# --- SoundCloud Safe Import ---
try:
    from .Soundcloud import SoundCloud
except Exception:
    class SoundCloud:
        def __init__(self):
            pass
        async def valid(self, *args, **kwargs):
            return False
        async def track(self, *args, **kwargs):
            return None, None
        async def download(self, *args, **kwargs):
            return None

# --- Spotify Safe Import ---
try:
    from .Spotify import Spotify
except Exception:
    class Spotify:
        def __init__(self):
            pass
        async def valid(self, *args, **kwargs):
            return False
        async def track(self, *args, **kwargs):
            return None, None
        async def playlist(self, *args, **kwargs):
            return []

# --- Telegram Safe Import ---
try:
    from .Telegram import Telegram
except Exception:
    class Telegram:
        def __init__(self):
            pass
        async def get_audio(self, *args, **kwargs):
            return None
        async def download(self, *args, **kwargs):
            return None

# --- YouTube Safe Import ---
try:
    from .Youtube import YouTube
except Exception:
    class YouTube:
        def __init__(self):
            pass
        async def exists(self, *args, **kwargs):
            return True
        async def url(self, *args, **kwargs):
            return ""
        async def title(self, *args, **kwargs):
            return "Audio Stream"
        async def duration(self, *args, **kwargs):
            return "00:00"
        async def thumbnail(self, *args, **kwargs):
            return ""
        async def track(self, *args, **kwargs):
            return "Audio Track", 0, ""
        async def formats(self, *args, **kwargs):
            return []
        async def slider(self, *args, **kwargs):
            return ""
        async def download(self, *args, **kwargs):
            return None


class PlaTForms:
    def __init__(self):
        self.apple = Apple()
        self.carbon = Carbon()
        self.saavn = Saavn()
        self.jiosaavn = self.saavn
        self.resso = Resso()
        self.soundcloud = SoundCloud()
        self.spotify = Spotify()
        self.telegram = Telegram()
        self.youtube = YouTube()
