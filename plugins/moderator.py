from plugin import Plugin
from functools import wraps
from decorators import command

import logging
import asyncio
import re

logs = logging.getLogger("discord")


class Moderator(Plugin):
    @staticmethod
    async def get_commands(server):
        commands = [
            {
                'name': '!clear [user] num',
                'description': 'Delete the last `num` messages. Optionally, out of the last `num` messages, delete '
                               'all made by `user`.'
            },
            {
                'name': '!mute user',
                'description': 'Mutes a user, preventing them from sending messages.'
            },
            {
                'name': '!unmute user',
                'description': 'Unmutes a muted user, allowing them to send messages.'
            }
        ]
        return commands

    @staticmethod
    async def check_auth(member):
        # Check if the author if authorized
        role_names = ['moderator']
        authorized = False
        for role in member.roles:
            authorized = any([role.name in role_names,
                             role.id in role_names,
                             role.permissions.manage_server])
            if authorized:
                break
        return authorized

    @command(pattern='^!clear ([0-9]*)$', require_one_of_roles="roles")
    async def clear_num(self, message, args):
        member = message.author
        check = await self.check_auth(member)
        if not check:
            return
        number = min(int(args[0]), 1000)
        if number < 1:
            return
        deleted_messages = await self.bot.purge_from(
            message.channel,
            limit=number+1
        )

        message_number = len(deleted_messages) - 1
        confirm_message = await self.bot.send_message(
            message.channel,
            "`Deleted {} message{}!`".format(
                message_number,
                "" if message_number < 2 else "s"
            )
        )
        await asyncio.sleep(3)

        await self.bot.delete_message(confirm_message)

    @command(pattern='^!clear <@!?([0-9]*)> ([0-9]*)$', require_one_of_roles="roles")
    async def clear_user(self, message, args):
        member = message.author
        check = await self.check_auth(member)
        if not check:
            return
        if not message.mentions:
            return
        user = message.mentions[0]
        if not user:
            return
        del_limit = int(args[1])

        deleted_messages = await self.bot.purge_from(
            message.channel,
            limit=del_limit,
            check=lambda m: m.author.id == user.id or m == message
        )

        message_number = len(deleted_messages)
        confirm = await self.bot.send_message(
            message.channel,
            "`Deleted {} messages!`".format(message_number)
        )
        await asyncio.sleep(3)
        await self.bot.delete_message(confirm)

    @command(pattern='^!mute <@!?([0-9]*)>$', require_one_of_roles="roles")
    async def mute(self, message, args):
        member = message.author
        check = await self.check_auth(member)
        if not check:
            return
        if not message.mentions:
            return
        member = message.mentions[0]
        check = await self.check_auth(member)
        if check:
            return

        allow, deny = message.channel.overwrites_for(member)
        allow.send_messages = False
        deny.send_messages = True
        await self.bot.edit_channel_permissions(
            message.channel,
            member,
            allow=allow,
            deny=deny
        )
        await self.bot.send_message(
            message.channel,
            "{} is now muted in this channel.".format(member.mention)
        )

    @command(pattern='^!unmute <@!?([0-9]*)>$', require_one_of_roles="roles")
    async def unmute(self, message, args):
        member = message.author
        check = await self.check_auth(member)
        if not check:
            return
        if not message.mentions:
            return
        member = message.mentions[0]

        check = await self.check_auth(member)
        if check:
            return

        allow, deny = message.channel.overwrites_for(member)
        allow.send_messages = True
        deny.send_messages = False
        await self.bot.edit_channel_permissions(
            message.channel,
            member,
            allow=allow,
            deny=deny
        )
        await self.bot.send_message(
            message.channel,
            "{} is no longer muted in this channel.".format(member.mention)
        )

    async def banned_words(self, message):
        banned_words = ""
        if banned_words:
            banned_words = banned_words.split(',')
        else:
            banned_words = []

        words = list(map(lambda w: w.lower(), message.content.split()))
        for banned_word in banned_words:
            if banned_word.lower() in words:
                await self.bot.delete_message(message)
                msg = await self.bot.send_message(
                    message.channel,
                    "{}, **LANGUAGE!!!**😡".format(
                        message.author.mention
                    )
                )
                await asyncio.sleep(3)
                await self.bot.delete_message(msg)
                return

    async def on_message_edit(self, before, after):
        await self.banned_words(after)

    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        await self.banned_words(message)
