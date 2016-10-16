from plugin import Plugin
import logging

logs = logging.getLogger('discord')


class BasicLogs(Plugin):
    is_global = True

    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            server, channel = message.server, message.channel
            logs.info("OUT >> {}#{} >> {}".format(
                server.name if not message.channel.is_private else "Private Message",
                channel.name if not message.channel.is_private else message.channel.id,
                message.clean_content.replace('\n', '~')
            ))
        return
