# All rights reserved.
#

import os
import random
from os.path import realpath

import aiohttp
from aiohttp import client_exceptions

try:
    from Fubuki.utils.exceptions import UnableToFetchCarbon
except Exception:
    class UnableToFetchCarbon(Exception):
        pass

themes = [
    "3024-night",
    "a11y-dark",
    "blackboard",
    "base16-dark",
    "base16-light",
    "cobalt",
    "duotone-dark",
    "dracula-pro",
    "hopscotch",
    "lucario",
    "material",
    "monokai",
    "nightowl",
    "nord",
    "oceanic-next",
    "one-light",
    "one-dark",
    "panda-syntax",
    "parasio-dark",
    "seti",
    "shades-of-purple",
    "solarized+dark",
    "solarized+light",
    "synthwave-84",
    "twilight",
    "verminal",
    "vscode",
    "yeti",
    "zenburn",
]

colour = [
    "#FF0000",
    "#FF5733",
    "#FFFF00",
    "#008000",
    "#0000FF",
    "#800080",
    "#A52A2A",
    "#FF00FF",
    "#D2B48C",
    "#00FFFF",
    "#808000",
    "#800000",
    "#00FFFF",
    "#30D5C8",
    "#00FF00",
    "#008080",
    "#4B0082",
    "#EE82EE",
    "#FFC0CB",
    "#000000",
    "#FFFFFF",
    "#808080",
]


class Carbon:
    def __init__(self):
        self.language = "auto"
        self.drop_shadow = True
        self.drop_shadow_blur = "68px"
        self.drop_shadow_offset = "20px"
        self.font_family = "JetBrains Mono"
        self.width_adjustment = True
        self.watermark = False

    async def generate(self, text: str, user_id):
        os.makedirs("cache", exist_ok=True)
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        ) as ses:
            params = {
                "code": text,
                "backgroundColor": random.choice(colour),
                "theme": random.choice(themes),
                "dropShadow": self.drop_shadow,
                "dropShadowOffsetY": self.drop_shadow_offset,
                "dropShadowBlurRadius": self.drop_shadow_blur,
                "fontFamily": self.font_family,
                "language": self.language,
                "watermark": self.watermark,
                "widthAdjustment": self.width_adjustment,
            }
            try:
                request = await ses.post(
                    "https://carbonara.solopov.dev/api/cook",
                    json=params,
                )
                if request.status != 200:
                    raise UnableToFetchCarbon("Failed to generate carbon image.")
                resp = await request.read()
            except (client_exceptions.ClientConnectorError, Exception) as e:
                raise UnableToFetchCarbon(f"Cannot reach Carbon host: {e}")

            out_path = f"cache/carbon{user_id}.jpg"
            with open(out_path, "wb") as f:
                f.write(resp)
            return realpath(out_path)
