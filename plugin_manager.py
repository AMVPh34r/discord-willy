import logging
from plugin import Plugin

log = logging.getLogger('discord')


class PluginManager:
    def __init__(self, bot):
        self.bot = bot
        self.bot.plugins = []

    def load(self, plugin):
        log.info('Loading plugin {}.'.format(plugin.__name__))
        plugin_instance = plugin(self.bot)
        self.bot.plugins.append(plugin_instance)
        log.info('Plugin {} loaded.'.format(plugin.__name__))

    def load_all(self):
        for plugin in Plugin.plugins:
            self.load(plugin)

    async def get_all(self, server):
        return self.bot.plugins
