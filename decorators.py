import re
import logging
import asyncio

from functools import wraps

log = logging.getLogger('discord')


def bg_task(sleep_time, ignore_errors=True):
    def actual_decorator(func):
        @wraps(func)
        async def wrapper(self):
            await self.bot.wait_until_ready()
            while True:
                if ignore_errors:
                    try:
                        await func(self)
                    except Exception as e:
                        log.info("An error occured in the {} bg task"
                                 " retrying in {} seconds".format(func.__name__,
                                                                  sleep_time))
                        log.info(e)
                else:
                    await func(self)

                await asyncio.sleep(sleep_time)

        wrapper._bg_task = True
        return wrapper

    return actual_decorator


def command(pattern=None, db_check=False, user_check=None, db_name=None,
            description="", usage=None):
    def actual_decorator(func):
        name = func.__name__
        cmd_name = "!" + name
        prog = re.compile(pattern or cmd_name)
        @wraps(func)
        async def wrapper(self, message):

            # Is it matching?
            match = prog.match(message.content)
            if not match:
                return

            args = match.groups()
            server = message.server
            author = message.author
            author_role_ids = [role.id for role in author.roles]

            is_admin = any([role.permissions.manage_server
                            for role in author.roles])

            # Checking the member with the predicate
            if user_check and not is_admin:
                authorized = await user_check(message.author)
                if not authorized:
                    return

            log.info("{}#{}@{} >> {}".format(message.author.name,
                                             message.author.discriminator,
                                             message.server.name,
                                             message.clean_content))

            await func(self, message, args)
        wrapper._db_check = db_check
        wrapper._db_name = db_name or func.__name__
        wrapper._is_command = True
        if usage:
            command_name = usage
        else:
            command_name = "!" + func.__name__
        wrapper.info = {"name": command_name,
                        "description": description}
        return wrapper
    return actual_decorator
