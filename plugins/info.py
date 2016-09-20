from plugin import Plugin
from decorators import command


class Info(Plugin):
    fancy_name = "Bot Info"

    @staticmethod
    async def get_commands(server):
        commands = [
            {
                'name': '!info',
                'description': 'Display bot info'
            },
            {
                'name': '!version',
                'description': 'Display current bot version'
            }
        ]
        return commands

    @command(pattern='^!(info(rmation)?)$')
    async def info(self, message, args):
        response = "Hi! I'm Digi Land's very own Willy! I decided to join the Discord server here in order to help " \
                   "out with some tasks and provide quick access to information on the world of Digis right here!" \
                   "\n\nWant to know what I'm capable of? Just enter `!help` for a list of commands I know!\n"

        await self.bot.send_message(message.channel, response)
        return

    @command(pattern='^!version$')
    async def version(self, message, args):
        response = "{}, v{}".format(self.bot.__name__, self.bot.__version__)
        await self.bot.send_message(message.channel, response)
        return
