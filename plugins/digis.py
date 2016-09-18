import aiohttp
import os
from plugin import Plugin
from decorators import command
from bs4 import BeautifulSoup

API_KEY = os.getenv('DIGIS_API_KEY')
BASE_URL = 'http://yaydigis.net/'
CDN_URL = 'http://cdn.yaydigis.net/'
API_URL = BASE_URL + 'api.php?key=' + API_KEY + '&'


class Digis(Plugin):
    fancy_name = 'Digis API'

    @staticmethod
    async def get_commands(server):
        commands = [
            {
                'name': '!info',
                'description': 'Display bot info'
            },
            {
                'name': '!userinfo user_id',
                'description': 'Show basic info on the user with the given ID'
            },
            {
                'name': '!usersearch query',
                'description': 'Search for users with usernames containing your query'
            },
            {
                'name': '!iteminfo item_id',
                'description': 'Show basic info on the item with the given ID'
            },
            {
                'name': '!itemsearch query',
                'description': 'Search for items with names containing your query'
            },
            {
                'name': '!colorinfo color_id',
                'description': 'Show basic info on the coloration with the given ID'
            },
            {
                'name': '!colorsearch query',
                'description': 'Search for colorations with names containing your query'
            },
            {
                'name': '!itemcount item_id',
                'description': 'See how many of a given item exist across Digis users'
            }
        ]
        return commands

    @staticmethod
    async def _api_get(method, query):
        with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"c": method,
                                                    "s": query,
                                                    "key": API_KEY}) as resp:
                data = await resp.json()
        return data

    @command(pattern='^!info$')
    async def info(self, message, args):
        response = "Hi! I'm Digi Land's very own Willy! I decided to join the Discord server here in order to help " \
                   "out with some tasks and provide quick access to information on the world of Digis right here!" \
                   "\n\nWant to know what I'm capable of? Just enter `!help` for a list of commands I know!\n"

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!version$')
    async def version(self, message, args):
        response = "{0}, v{1}".format(
            self.bot.__name__, self.bot.__version__
        )
        await self.bot.send_message(message.channel, response)

    @command(pattern='^!userinfo #?([0-9]*)$')
    async def user_info(self, message, args):
        user_id = args[0]
        data = await self._api_get('userinfo', user_id)

        response_template = "Here's what I could dig up on user #{0}:\n" \
                            "**Username:** {1}\n" \
                            "**Profile Link:** {2}p_user_profile.php?ID={3}\n" \
                            "**Forum Posts:** {2}forum_history_user.php?ID={3}"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']
        response = response_template.format(
            user_id,
            result['username'],
            BASE_URL, user_id
        )

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!usersearch (.*)$')
    async def user_search(self, message, args):
        query = args[0]
        data = await self._api_get('usersearch', query)

        response_template = "I found {0} results for \"{1}\"{2}"
        result_template = "    {0} (#{1})\n"
        info_template = "Tell me `!userinfo USER_ID` if you want more info!"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']

        response = response_template.format(
            len(result), query, ":\n" if len(result) > 0 else ""
        )
        for user in result:
            response += result_template.format(
                user['username'], user['userID']
            )
        if len(result) > 0:
            response += info_template

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!iteminfo #?([0-9]*)$')
    async def item_info(self, message, args):
        item_id = args[0]
        data = await self._api_get('iteminfo', item_id)

        response_template = "__{0}__\n" \
                            "**Item Description:** {1}\n" \
                            "**Artist:** {2} (#{3})\n" \
                            "**Price:** {4}{5}"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']
        response = response_template.format(
            result['iName'],
            result['iDesc'],
            result['artistname'], result['artist'],
            result['price'], "GCC" if result['price'] is not None else ""
        )

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!itemsearch (.*)$')
    async def item_search(self, message, args):
        query = args[0]
        data = await self._api_get('itemsearch', query)

        response_template = "I've got {0} results for \"{1}\"{2}"
        result_template = "    {0} (#{1})\n"
        info_template = "Send `!iteminfo ITEM_ID` for more."

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']

        response = response_template.format(
            len(result), query, ":\n" if len(result) > 0 else ""
        )
        for item in result:
            response += result_template.format(
                item['iName'], item['itemID']
            )
        if len(result) > 0:
            response += info_template

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!colorinfo #?([0-9]*)$')
    async def color_info(self, message, args):
        color_id = args[0]
        data = await self._api_get('colorinfo', color_id)

        species = {
            'N': 'Nibble',
            'A': 'Agwee',
            'C': 'Coffee',
            'Z': 'Zafrii'
        }
        response_template = "__{0}__\n" \
                            "**Species:** {1}\n" \
                            "**Artist:** {2} (#{3})\n" \
                            "**Images:** \n" \
                            "{4}pets/pet_{5}Fb.png\n" \
                            "{4}pets/pet_{5}Mb.png"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']
        response = response_template.format(
            result['colorName'],
            species[result['species']],
            result['artistname'], result['artist'],
            CDN_URL, result['img']
        )

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!colorsearch (.*)$')
    async def color_search(self, message, args):
        query = args[0]
        data = await self._api_get('colorsearch', query)

        response_template = "Looks like we have {0} results for \"{1}\"{2}"
        result_template = "    {0} (#{1})\n"
        info_template = "Tell me `!colorinfo COLOR_ID` for more info!"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']

        response = response_template.format(
            len(result), query, ":\n" if len(result) > 0 else ""
        )
        for color in result:
            response += result_template.format(
                color['colorName'], color['colorID']
            )
        if len(result) > 0:
            response += info_template

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!itemcount #?([0-9]*)$')
    async def item_count(self, message, args):
        item_id = args[0]
        data = await self._api_get('itemcount', item_id)

        response_template = "Hmm... let's see...\n" \
                            "I found {0} {1}{2} among all users!"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']
        response = response_template.format(
            result['num_items'], result['iName'], "'" if result['iName'].endswith('s') else "s"
        )

        await self.bot.send_message(message.channel, response)
