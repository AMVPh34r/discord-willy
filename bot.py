from willy import Willy
import os
import logging

from plugins.digis import Digis

# Global plugins
from plugins.basiclogs import BasicLogs

token = os.getenv('BOT_TOKEN')
bot_debug = os.getenv('BOT_DEBUG')
if bot_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

bot = Willy()
bot.run(token)
