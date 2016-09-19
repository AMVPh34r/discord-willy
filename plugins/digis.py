import aiohttp
import os
from plugin import Plugin
from decorators import command

API_KEY = os.getenv('DIGIS_API_KEY')
BASE_URL = 'http://yaydigis.net/'
CDN_URL = 'http://cdn.yaydigis.net/'
API_URL = '{0}api.php?key={1}&'.format(
    BASE_URL, API_KEY
)


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
            },
            {
                'name': '!rules',
                'description': 'Get a quick link to the Digis rules and ToS'
            },
            {
                'name': '!faq [topic]',
                'description': 'Get an answer to a frequently asked question, or a link to the online FAQ page'
            }
        ]
        return commands

    @staticmethod
    async def _api_get(method, query=''):
        with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"c": method,
                                                    "s": query,
                                                    "key": API_KEY}) as resp:
                data = await resp.json()
        return data

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
        return

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
        return

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
            result['price'], " GCC" if result['price'] is not None else ""
        )

        await self.bot.send_message(message.channel, response)
        return

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
        return

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
        return

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
        return

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
        return

    @command(pattern='^!rules$')
    async def rules(self, message, args):
        response_template = "Don't forget to read up on the Digis rules and ToS!\n" +\
            "{0}\n" +\
            "{1}"
        response = response_template.format(
            BASE_URL + "p_rules.php",
            BASE_URL + "p_ToS.php"
        )

        await self.bot.send_message(message.channel, response)
        return

    @command(pattern='^!faq ?(.*)$')
    async def faq(self, message, args):
        question = args[0].lower()

        faqs = {
            "trading": "Digi trading costs `{0} GCC` for a standard trade and `{1} GCC` for a one-way trade.".format(
                "500", "12.5k"
            ),
            "fotm": "You can check out this month's flavor of the month and buy items here:\n{0}".format(
                BASE_URL + "p_item_buy.php"
            ),
            "dailies": "Looking for free stuff? Check out our dailies once per day!\n{0}".format(
                BASE_URL + "p_help_dg_dailies.php"
            ),
            "interest": "Bank interest rates begin at `{0}%`, and decrease for higher bank balances, to a minimum "
                        "of `{1}%`.".format(
                8, 4
            ),
            "staff": "Here's a list of all the current Digis staff members! Aren't they all wonderful?\n{0}".format(
                BASE_URL + "p_staff.php"
            ),
            "news": "Check out the latest Digis news updates!\n{0}".format(
                BASE_URL + "p_news.php"
            ),
            "petprices": "Pets start at `{0} GCC`, and the price increases as you obtain more pets. The equation for "
                         "pet cost is `{1}`, and there is a cap of `{2} GCC`.".format(
                200, "(D²+1)*200", "20k"
            ),
            "botidea": "Got a feature idea or request for the bot? Let us know via the GitHub issue tracker!\n"
                       "{0}".format(
                "https://github.com/AMVPh34r/discord-willy/issues"
            )
        }

        if question == "":
            response = "Here's a list of FAQ topics I can tell you about (just send me `!faq topic` for more):\n" \
                       "`{0}`\n" \
                       "You can read up on the site FAQ here: {1}".format(
                            ', '.join(sorted(faqs.keys())),
                            BASE_URL + "p_help_faq.php"
                        )
        elif question in faqs.keys():
            response = faqs[question]
        else:
            response_template = "Sorry! I couldn't find an answer for you. You might have better luck reading " \
                                "through the FAQ page online: {0}"
            response = response_template.format(
                BASE_URL + "p_help_faq.php"
            )

        await self.bot.send_message(message.channel, response)
        return

    @command(pattern='^!time')
    async def time(self, message, args):
        data = await self._api_get('time')

        response_template = "The current Digis time is `{}`"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']

        response = response_template.format(
            result['time']
        )

        await self.bot.send_message(message.channel, response)
        return

    @command(pattern='^!fotm')
    async def fotm(self, message, args):
        data = await self._api_get('fotm')

        response_template = "Here's {month}'s FotM!\n" \
                            "__{name} (#{id})__\n" \
                            "**Potion:** {potion} (#{potion_id})\n" \
                            "**Items:**\n" \
                            "    {item1} (#{item1_id})\n" \
                            "    {item2} (#{item2_id})\n" \
                            "**Image:** {img_url}.jpg\n" \
                            "Want to buy? Check out our FotM and IRL shops!\n" \
                            "    {fotm_shop_url}\n" \
                            "    {irl_shop_url}"

        if data['success'] is False:
            response = "Error{0}".format(
                ": `{}`".format(data['message']) if data['message'] else ""
            )
            await self.bot.send_message(message.channel, response)
            return
        result = data['result']

        response = response_template.format(
            month=result['month_name'],
            name=result['name'], id=result['colorId'],
            potion=result['potionName'], potion_id=result['potionId'],
            item1=result['item1Name'], item1_id=result['item1Id'],
            item2=result['item2Name'], item2_id=result['item2Id'],
            img_url="{}news/img/fotm/{}.jpg".format(
                BASE_URL, result['fotm_image']
            ),
            fotm_shop_url="{}p_item_buy.php".format(
                BASE_URL
            ),
            irl_shop_url="{}p_shop_irl.php".format(
                BASE_URL
            )
        )

        await self.bot.send_message(message.channel, response)
        return
