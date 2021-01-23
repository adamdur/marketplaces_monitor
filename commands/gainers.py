import settings
import discord

from commands.base_command import BaseCommand

from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Gainers(BaseCommand):

    def __init__(self):
        description = "Shows list of top price and demand gainers"
        params = []
        params_optional = ['buy_sell', 'renewal']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.hbt0417dv97p'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        type = common_helper.get_optional_param_by_index(params_optional, 0, "wtb")
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 1, "renewal")
        if type == "wtb":
            type_opposite = "wts"
        elif type == "wts":
            type_opposite = "wtb"

        if not await errors_helper.check_type_param(type, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_renewal_param(renewal_param, message.channel, guide=self.guide):
            return
        renewal = common_helper.get_renewal_param_value(renewal_param)

        waiting_message = await message.channel.send('Gathering data, please wait...')

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_gainers(db, type, renewal)

        if not await errors_helper.check_db_response(data, message.channel):
            return await waiting_message.delete()
        if not data['current'] or not data['prev']:
            return await waiting_message.edit(content=":exclamation: No sufficient data found. Try again later...")

        current_data = data['current']
        prev_data = data['prev']

        demand_data = {}
        price_data = {}
        for row in current_data:
            try:
                if row['count'] > 10:
                    demand_data[row['bot']][f"current_{row['type']}"] = row['count']
                    price_data[row['bot']][f"current_{row['type']}"] = row['price']
            except KeyError:
                if row['count'] > 10:
                    demand_data[row['bot']] = {f"current_{row['type']}": row['count']}
                    price_data[row['bot']] = {f"current_{row['type']}": row['price']}
        for row in prev_data:
            try:
                demand_data[row['bot']][f"prev_{row['type']}"] = row['count']
                price_data[row['bot']][f"prev_{row['type']}"] = row['price']
            except KeyError:
                continue

        filtered_demand_data = {}
        for item in demand_data.items():
            key, d = item
            try:
                curr_type = d[f"current_{type}"]
                if curr_type < 10:
                    continue
                prev_type = d[f"prev_{type}"]
                curr_type_opposite = d[f"current_{type_opposite}"]
                prev_type_opposite = d[f"prev_{type_opposite}"]
                total = curr_type + curr_type_opposite
                total_prev = prev_type + prev_type_opposite

                percentage = get_percentage(curr_type, total)
                percentage_prev = get_percentage(prev_type, total_prev)
                movement = get_movement_int(percentage, percentage_prev)
            except KeyError:
                continue

            filtered_demand_data[key] = {'movement': movement, 'curr': curr_type, 'prev': prev_type}

        filtered_price_data = {}
        for item in price_data.items():
            key, d = item
            try:
                curr_type = d[f"current_{type}"]
                prev_type = d[f"prev_{type}"]
                curr_type_opposite = d[f"current_{type_opposite}"]
                prev_type_opposite = d[f"prev_{type_opposite}"]
                total = curr_type + curr_type_opposite
                total_prev = prev_type + prev_type_opposite

                percentage = get_percentage(curr_type, total)
                percentage_prev = get_percentage(prev_type, total_prev)
                movement = get_movement_int(percentage, percentage_prev)
            except KeyError:
                continue

            filtered_price_data[key] = {'movement': movement, 'curr': curr_type, 'prev': prev_type}

        def keyfunc(tup):
            key, d = tup
            return d['movement']

        demand_data_sorted = sorted(filtered_demand_data.items(), key=keyfunc, reverse=True)
        price_data_sorted = sorted(filtered_price_data.items(), key=keyfunc, reverse=True)

        embed = discord.Embed(
            title=f"LIST OF TOP GAINERS IN {type.upper()} DEMAND & PRICING",
            description="",
            color=settings.DEFAULT_EMBED_COLOR
        )
        embed.add_field(name="\u200b", value="**DEMAND**", inline=False)
        idx = 1
        for item in demand_data_sorted[:9]:
            bot = item[0]
            movement_text = get_movement_text(item[1]["movement"], item[1]["curr"])
            embed.add_field(name=f"{idx}. {bot.capitalize()}", value=f"{movement_text}", inline=True)
            idx += 1

        embed.add_field(name="\u200b", value="**PRICING**", inline=False)
        idx = 1
        for item in price_data_sorted[:9]:
            bot = item[0]
            movement_text = get_movement_text(item[1]["movement"], item[1]["curr"], True, "$")
            embed.add_field(name=f"{idx}. {bot.capitalize()}", value=f"{movement_text}", inline=True)
            idx += 1

        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        return await waiting_message.edit(content="", embed=embed)


def round_price(x, base=10):
    return base * round(x/base)


def get_icon(percentage, value=0):
    if percentage == value:
        return ":white_circle:"
    elif percentage > value:
        return ":green_circle:"
    elif percentage < value:
        return ":red_circle:"


def get_percentage(value, total, dec=2):
    return round(value / (total / 100), dec)


def get_percentage_clean(value, total):
    return value / (total / 100)


def get_movement_text(movement, value, round_value=False, value_prefix=""):
    if round_value:
        value = 10 * round(value/10)
    if movement == 0:
        return f":white_circle: **{movement}%** | {value_prefix}{value}"
    elif movement > 0:
        return f":green_circle: **+{movement}%** | {value_prefix}{value}"
    elif movement < 0:
        return f":red_circle: **{movement}%** | {value_prefix}{value}"


def get_movement_int(current, prev=None, dec=2):
    movement = current
    if prev:
        movement = current - prev
    return round(movement, dec)
