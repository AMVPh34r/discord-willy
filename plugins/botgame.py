from plugin import Plugin
import discord
import os


class BotGame(Plugin):
    is_global = True
    game_name = os.getenv("BOT_GAME")
    game = None

    async def on_ready(self):
        if self.game_name:
            self.game = discord.Game(name=self.game_name)
        await self.bot.change_status(self.game)
