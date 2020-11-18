import settings
import discord
import math

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


def get_bot_price_value(data, bot, type):
    try:
        value = '{:.0f}'.format(data[bot][type])
    except KeyError:
        value = 'N/A'
    return value


class Pricing_stats(BaseCommand):

    def __init__(self):
        description = "Shows bots pricing stats"
        params = []
        params_optional = ['days', 'renewal']
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return
        days = common_helper.get_optional_param_by_index(params_optional, 0, "1")
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 1, "renewal")

        if not await errors_helper.check_renewal_param(renewal_param, message.channel):
            return
        if not await errors_helper.check_days_param(days, message.channel):
            return

        renewal = common_helper.get_renewal_param_value(renewal_param)

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_pricing_stats(db, days, renewal)

        if not await errors_helper.check_db_response(data, message.channel):
            return

        index = 0
        stats_str = ''
        stats_str_scnd = ''
        stats_str_thrd = ''
        days_str = common_helper.get_time_string_from_days(days)
        description = "**{} bots pricing stats from last {} and its movement:**\n>>> S = WTS\nB = WTB"
        embed = discord.Embed(title="{} PRICING STATS".format(renewal_param.upper()), description=description.format(renewal_param.upper(), days_str), color=settings.DEFAULT_EMBED_COLOR)

        for bot, values in data.items():
            wts_value = get_bot_price_value(data, bot, 'wts')
            wtb_value = get_bot_price_value(data, bot, 'wtb')
            wts_value_past = get_bot_price_value(data, bot, 'wts_past')
            wtb_value_past = get_bot_price_value(data, bot, 'wtb_past')

            movement_wts = common_helper.get_movement(wts_value, wts_value_past)
            movement_wtb = common_helper.get_movement(wtb_value, wtb_value_past)

            wts_value = '$' + wts_value if wts_value.isdigit() else wts_value
            wtb_value = '$' + wtb_value if wtb_value.isdigit() else wtb_value
            movement_wts = '{}{:.1f}%'.format('+' if movement_wts > 0 else '', movement_wts) if isinstance(movement_wts, float) or isinstance(movement_wts, int) else movement_wts
            movement_wtb = '{}{:.1f}%'.format('+' if movement_wtb > 0 else '', movement_wtb) if isinstance(movement_wtb, float) or isinstance(movement_wtb, int) else movement_wtb

            msg = '{}\n> S: {} **[{}]**\n> B: {} **[{}]**\n'.format(bot.capitalize(), wts_value, movement_wts, wtb_value, movement_wtb)
            if index < math.ceil(len(data) / 3):
                stats_str += msg
            elif math.ceil(len(data) / 3) <= index < math.ceil(len(data) / 3) * 2:
                stats_str_scnd += msg
            else:
                stats_str_thrd += msg
            index += 1

        embed.add_field(name="\u200b", value=stats_str, inline=True)
        embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        embed.add_field(name="\u200b", value=stats_str_thrd, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
