# All rights reserved.

from Fubuki.core.bot import AyuBot
from Fubuki.core.dir import dirr
from Fubuki.core.git import git
from Fubuki.core.userbot import Userbot
from Fubuki.misc import dbb, sudo

from .logging import LOGGER

# Directories
dirr()

# Check Git Updates
git()

# Initialize Memory DB
dbb()

# Load Sudo Users from DB
sudo()

# Bot Client
app = AyuBot()

# Assistant Client
userbot = Userbot()

from .platforms import PlaTForms

Platform = PlaTForms()
HELPABLE = {}
