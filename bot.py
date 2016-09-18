from willy import Willy
import os
import logging

from plugins.help import Help
from plugins.info import Info
from plugins.digis import Digis
from plugins.moderator import Moderator

# Global plugins
from plugins.basiclogs import BasicLogs
from plugins.botgame import BotGame

token = os.getenv('BOT_TOKEN')
bot_debug = os.getenv('BOT_DEBUG')
if bot_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

bot = Willy()
bot.run(token)
