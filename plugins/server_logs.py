import logging
import os
from plugin import Plugin

LOG_DIR = os.getenv('LOG_DIR')

logs = logging.getLogger('discord')


class ServerLogs(Plugin):
    async def on_message(self, message):
        if not LOG_DIR:
            return

        log_msg = "{} - {}: {}".format(
            message.timestamp.strftime(
                '%H:%M:%S'
            ), message.author.name, message.content
        )
        log_fulldir = "{dir}{s}{srv}{s}{chn}{s}".format(
            dir=LOG_DIR,
            s=os.sep,
            srv=message.server.id,
            chn=message.channel.name,
            date=message.timestamp.strftime(
                '%Y-%m-%d'
            )
        )
        log_fname = "{}.txt".format(message.timestamp.strftime('%Y-%m-%d'))
        log_fullpath = "{d}{s}{f}".format(
            d=log_fulldir,
            s=os.sep,
            f=log_fname
        )

        if not os.path.exists(log_fulldir):
            os.makedirs(log_fulldir)
        with open(log_fullpath, 'a') as log_file:
            log_file.write("{}\n".format(log_msg))
        return
