# Fubuki Music Bot Engine
# System stats optimizer tailored for Android/Termux & Snapdragon 680

import os
import time
import psutil

from Fubuki.misc import _boot_
from .formatters import get_readable_time


async def bot_sys_stats():
    bot_uptime = int(time.time() - _boot_)
    up = f"{get_readable_time(bot_uptime)}"
    cpu = f"{psutil.cpu_percent(interval=0.2)}%"
    ram = f"{psutil.virtual_memory().percent}%"

    # Termux/Android friendly disk usage detection
    target_path = os.getenv("PREFIX", "/")
    if not os.path.exists(target_path):
        target_path = "/"

    try:
        disk = f"{psutil.disk_usage(target_path).percent}%"
    except Exception:
        disk = "N/A"

    return up, cpu, ram, disk
