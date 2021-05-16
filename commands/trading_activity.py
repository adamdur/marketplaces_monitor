import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Trading_activity(BaseCommand):

    def __init__(self):
        description = "Shows current trading activity of whole marker or for selected bot"
        params = []
        params_optional = ['bot', 'renewal']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.hbt0417dv97p'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        bot = common_helper.get_optional_param_by_index(params_optional, 0)
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 1, "renewal")

        if bot:
            if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
                return
            if not await errors_helper.check_renewal_param(renewal_param, message.channel, guide=self.guide):
                return
        renewal = common_helper.get_renewal_param_value(renewal_param)
        waiting_message = await message.channel.send('Gathering data, please wait...')

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_trading_activity_slim(db, bot, renewal)

        if not data['current'] or not data['prev']:
            return await waiting_message.edit(content=":exclamation: No sufficient data found for. Try again later...")
        if not await errors_helper.check_db_response(data, message.channel):
            return await waiting_message.delete()

        wtb_count = wts_count = wtb_count_prev = wts_count_prev = 0
        wtb_price = wts_price = wtb_price_prev = wts_price_prev = 0
        for row in data['current']:
            if row['type'] == 'wtb':
                wtb_count = row['count']
                wtb_price = row['price']
            elif row['type'] == 'wts':
                wts_count = row['count']
                wts_price = row['price']
        for row in data['prev']:
            if row['type'] == 'wtb':
                wtb_count_prev = row['count']
                wtb_price_prev = row['price']
            elif row['type'] == 'wts':
                wts_count_prev = row['count']
                wts_price_prev = row['price']

        total_count = wtb_count + wts_count
        total_count_prev = wtb_count_prev + wts_count_prev

        if total_count == 0 or total_count_prev == 0:
            return await waiting_message.edit(content=":exclamation: No sufficient data found for. Try again later...")

        description = ""
        # if wtb_count == wts_count:
        #     description += "Trading activity is currently **Stagnant**"
        # elif wtb_count > wts_count:
        #     description += "Trading activity is currently in state of **Seller's market**"
        # elif wtb_count < wts_count:
        #     description += "Trading activity is currently in state of **Buyer's market**"
        if abs(wtb_count - wts_count) < 3:
            description += "Trading activity is currently **Stagnant**"
        elif wtb_count - wts_count >= 3:
            description += "Trading activity is currently in state of **Seller's market**"
        elif wtb_count - wts_count <= -3:
            description += "Trading activity is currently in state of **Buyer's market**"
        embed = discord.Embed(
            title=f"TRADING ACTIVITY STATS{' FOR {}'.format(bot.upper()) if bot else ''}",
            description=description,
            color=settings.DEFAULT_EMBED_COLOR
        )

        buy_percentage = get_percentage(wtb_count, total_count)
        sell_percentage = get_percentage(wts_count, total_count)
        buy_percentage_prev = get_percentage(wtb_count_prev, total_count_prev)
        sell_percentage_prev = get_percentage(wts_count_prev, total_count_prev)

        buy_movement = get_movement(buy_percentage, buy_percentage_prev)
        sell_movement = get_movement(sell_percentage, sell_percentage_prev)

        buy_price_movement = common_helper.get_movement_clean(wtb_price, wtb_price_prev)
        sell_price_movement = common_helper.get_movement_clean(wts_price, wts_price_prev)

        # buy_icon = get_icon(buy_percentage, 50)
        # sell_icon = get_icon(sell_percentage, 50)
        buy_icon = get_icon(buy_percentage - buy_percentage_prev)
        sell_icon = get_icon(sell_percentage - sell_percentage_prev)
        buy_price_icon = get_icon(buy_price_movement)
        sell_price_icon = get_icon(sell_price_movement)

        embed.add_field(name=f"**{buy_icon} BUYERS {buy_percentage}%**", value=f"{buy_movement}", inline=True)
        embed.add_field(name=f"**{sell_icon} SELLERS {sell_percentage}%**", value=f"{sell_movement}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name=f"**{buy_price_icon} BUY VOLUME ${round_price(wtb_price)}**", value=f"{get_movement(round(buy_price_movement, 2))}", inline=True)
        embed.add_field(name=f"**{sell_price_icon} SELL VOLUME ${round_price(wts_price)}**", value=f"{get_movement(round(sell_price_movement, 2))}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await message.channel.send(embed=embed)
        await waiting_message.delete()


def round_price(x, base=10):
    return base * round(x/base)


def get_icon(percentage, value=0):
    if percentage == value:
        return ":white_circle:"
    elif percentage > value:
        return ":green_circle:"
    elif percentage < value:
        return ":red_circle:"


def get_percentage(value, total):
    return round(value / (total / 100))


def get_movement(current, prev=None):
    movement = current
    if prev:
        movement = current - prev
    if movement == 0:
        return "No movement"
    elif movement > 0:
        return f":chart_with_upwards_trend: +{movement}%"
    elif movement < 0:
        return f":chart_with_downwards_trend: {movement}%"
