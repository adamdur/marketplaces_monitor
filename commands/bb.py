import settings
import discord

from datetime import datetime
from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import common as common_helper
from helpers import errors as errors_helper
from helpers import bb_api as botbroker


class Bb(BaseCommand):

    def __init__(self):
        description = "BotBroker command"
        params = ['bot']
        params_optional = ['renewal']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.6kgyhrr3b7o6'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        bot = common_helper.get_param_by_index(params, 0)
        renewal = common_helper.get_optional_param_by_index(params_optional, 0, "renewal")

        bot = await errors_helper.check_bb_bot_param(bot, message.channel, guide=self.guide)
        if not bot:
            return
        if not await errors_helper.check_bb_renewal_param(renewal, message.channel, guide=self.guide):
            return

        waiting_message = await message.channel.send('Gathering data, please wait...')
        data = await botbroker.get_bot_data(bot, renewal, waiting_message)

        asks_data = data['asks']['data']
        bids_data = data['bids']['data']
        sales_data = data['sales']['data']
        asks_total_count = data['asks']['total_count']
        bids_total_count = data['bids']['total_count']
        sales_total_count = data['sales']['total_count']

        if not asks_data and not bids_data and not sales_data:
            return await waiting_message.edit(content=":exclamation: No sufficient data found for {}. Try again later...".format(bot['name'].upper()))

        embed = discord.Embed(title="BOTBROKER {} {} ACTIVITY STATS".format(bot['name'].upper(), renewal.upper()), description="View {} on [**BotBroker.io**]({})".format(bot['name'], settings.BB_BASE_URL + bot['url']), color=settings.DEFAULT_EMBED_COLOR)
        embed.set_thumbnail(url=bot['image'])
        if asks_data:
            msg = ''
            index = 1
            for ask in asks_data[:10]:
                msg += '{}. **${}**{}\n'.format(index, ask['price'], '\u2002|\u2002*({})*'.format(ask['specification']) if ask['specification'] else '')
                index += 1
            embed.add_field(name="**Lowest asks:**", value=msg, inline=True)
        if bids_data:
            msg = ''
            index = 1
            for bid in bids_data[:10]:
                msg += '{}. **${}**{}\n'.format(index, bid['price'], '\u2002|\u2002*({})*'.format(bid['specification']) if bid['specification'] else '')
                index += 1
            embed.add_field(name="**Highest bids:**", value=msg, inline=True)
        if sales_data:
            msg = ''
            index = 1
            for sale in sales_data[:10]:
                msg += '{}\u2002|\u2002**${}**{}\n'.format(datetime.fromtimestamp(sale['matched_at']).strftime("%Y-%m-%d"), sale['price'], '\u2002|\u2002*({})*'.format(sale['specification']) if sale['specification'] else '')
                index += 1
            embed.add_field(name="**Last sales:**", value=msg, inline=False)
        if asks_total_count:
            embed.add_field(name="**Total asks count:**", value=asks_total_count, inline=True)
        if bids_total_count:
            embed.add_field(name="**Total bids count:**", value=bids_total_count, inline=True)
        if sales_total_count:
            embed.add_field(name="**Total sales count:**", value=sales_total_count, inline=True)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await waiting_message.edit(content='', embed=embed)
