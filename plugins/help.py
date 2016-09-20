from plugin import Plugin
import logging
import re

log = logging.getLogger('discord')

async def get_help_info(self, server):
    if self.fancy_name is None:
        self.fancy_name = type(self).__name__

    commands = []
    if hasattr(self, "get_commands"):
        commands += await self.get_commands(server)
    else:
        for cmd in self.commands.values():
            commands.append(cmd.info)
    payload = {
        'name': type(self).__name__,
        'fancy_name': self.fancy_name,
        'commands': commands
    }
    return payload


class Help(Plugin):
    regex = r'^!(help|commands|cmds)$'

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        # Patch the Plugin class
        Plugin.get_help_info = get_help_info

    async def generate_help(self, server):
        enabled_plugins = await self.bot.plugin_manager.get_all(server)
        enabled_plugins = sorted(enabled_plugins, key=lambda p: type(p).__name__)

        help_payload = []
        for plugin in enabled_plugins:
            if not isinstance(plugin, Help):
                help_info = await plugin.get_help_info(server)
                help_payload.append(help_info)

        return self.render_message(help_payload)

    @staticmethod
    def render_message(help_payload):
        message_batches = [""]
        for plugin_info in help_payload:
            if plugin_info['commands']:
                message = "**{}**\n".format(plugin_info['fancy_name'])
                if len(message_batches[-1] + message) > 2000:
                    message_batches.append(message)
                else:
                    message_batches[-1] += message
            for cmd in plugin_info['commands']:
                message = "   **{}** {}\n".format(cmd['name'], cmd.get('description', ''))
                if len(message_batches[-1] + message) > 2000:
                    message_batches.append(message)
                else:
                    message_batches[-1] += message
        return message_batches

    async def on_message(self, message):
        if re.search(self.regex, message.content):
            log.info('{}#{}@{} >> !help'.format(
                message.author.name,
                message.author.discriminator,
                message.server.name
            ))
            server = message.server
            help_messages = await self.generate_help(server)
            if help_messages == [""]:
                help_messages = ["There's no command to show"]
            destination = message.channel
            for msg in help_messages:
                await self.bot.send_message(destination, msg)
        return
