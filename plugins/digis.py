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
    fancy_name='Digis API'

    async def get_commands(self, server):
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
            }
        ]
        return commands

    async def _api_get(self, method, query):
        with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"c": method,
                                                    "s": query,
                                                    "key": API_KEY}) as resp:
                data = await resp.json()
        return data

    @command(pattern='^!info$')
    async def info(self, message, args):
        response = "Hi! I'm Digi Land's very own Willy! I decided to join the Discord server here in order to help " + \
                   "out with some tasks and provide quick access to information on the world of Digis right here!" + \
                   "\n\nHere's a quick rundown of what I can do now (and I'm always learning new tricks):\n"
        response += "`!userinfo USER_ID` Give me the ID number of a Digis user and I can display some basic " + \
                    "profile information about them, as well as some helpful links. Not sure what a user's ID is? " +\
                    "Don't worry!\n"
        response += "`!usersearch QUERY` Give me all or part of someone's username and I can fetch their ID for you!\n"
        response += "`!iteminfo ITEM_ID` Given an item's ID, I'll display that item's name and information!\n"
        response += "`!itemsearch QUERY` Just like with users, I can help you track down an item if you don't know " + \
                    "its ID or full name!\n"
        response += "`!colorinfo COLOR_ID` Want to see how a certain pet coloration looks? Just holler and I'll " + \
                    "give you some beautiful pictures as well as information on the coloration of your choice!\n"
        response += "`!colorsearch QUERY` And of course if you don't know the coloration's ID off the top of your " + \
                    "head (I certainly don't blame you), I can help you find it here!"

        await self.bot.send_message(message.channel, response)

    @command(pattern='^!userinfo #?([0-9]*)$')
    async def user_info(self, message, args):
        user_id = args[0]
        data = await self._api_get('userinfo', user_id)

        response_template = "Info for user #{0}:\n" +\
            "**Username:** {1}\n" + \
            "**Profile Link:** {2}p_user_profile.php?ID={3}\n" + \
            "**Forum Posts:** {2}forum_history_user.php?ID={3}"

        if data['success'] is False:
            response = "Error" + (": `" + data['message'] + "`" if data['message'] else "")
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

        response_template = "{0} results for \"{1}\"{2}"
        result_template = "    {0} (#{1})\n"
        info_template = "Enter `!userinfo USER_ID` for more."

        if data['success'] is False:
            response = "Error" + (": `" + data['message'] + "`" if data['message'] else "")
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

        response_template = "__{0}__\n" +\
            "**Item Description:** {1}\n" +\
            "**Artist:** {2} (#{3})\n" +\
            "**Price:** {4}{5}"

        if data['success'] is False:
            response = "Error" + (": `" + data['message'] + "`" if data['message'] else "")
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

        response_template = "{0} results for \"{1}\"{2}"
        result_template = "    {0} (#{1})\n"
        info_template = "Enter `!iteminfo ITEM_ID` for more."

        if data['success'] is False:
            response = "Error" + (": `" + data['message'] + "`" if data['message'] else "")
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
        response_template = "__{0}__\n" +\
            "**Species:** {1}\n" +\
            "**Artist:** {2} (#{3})\n" +\
            "**Images:** \n" +\
            "{4}pets/pet_{5}Fb.png\n" +\
            "{4}pets/pet_{5}Mb.png"

        if data['success'] is False:
            response = "Error" + (": `" + data['message'] + "`" if data['message'] else "")
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

        response_template = "{0} results for \"{1}\"{2}"
        result_template = "    {0} (#{1})\n"
        info_template = "Enter `!colorinfo COLOR_ID` for more."

        if data['success'] is False:
            response = "Error" + (": `" + data['message'] + "`" if data['message'] else "")
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
