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
        return None
    return value


class Pricing_stats(BaseCommand):

    def __init__(self):
        description = "Shows bots pricing stats"
        params = []
        params_optional = ['renewal', 'days']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.h62bylwh8ylu'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 0, "renewal")
        days = common_helper.get_optional_param_by_index(params_optional, 1, "1")

        if not await errors_helper.check_renewal_param(renewal_param, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_days_param(days, message.channel, guide=self.guide):
            return

        renewal = common_helper.get_renewal_param_value(renewal_param)

        waiting_message = await message.channel.send('Gathering data, please wait...')
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_pricing_stats(db, days, renewal)

        if not await errors_helper.check_db_response(data, message.channel):
            return await waiting_message.delete()

        index = 0
        stats_str = ''
        stats_str_scnd = ''
        stats_str_thrd = ''
        days_str = common_helper.get_time_string_from_days(days)
        description = "**{} bots pricing stats from last {} and its movement:**\n>>> S = WTS\nB = WTB"
        embed = discord.Embed(title="{} PRICING STATS".format(renewal_param.upper()), description=description.format(renewal_param.upper(), days_str), color=settings.DEFAULT_EMBED_COLOR)

        filtered_data = {}
        for bot, values in data.items():
            try:
                test1 = data[bot]['wts']
                test2 = data[bot]['wtb']
                test3 = data[bot]['wts_past']
                test4 = data[bot]['wtb_past']
                filtered_data[bot] = values
            except KeyError:
                continue

        for bot, values in filtered_data.items():
            wts_value = get_bot_price_value(filtered_data, bot, 'wts')
            wtb_value = get_bot_price_value(filtered_data, bot, 'wtb')
            wts_value_past = get_bot_price_value(filtered_data, bot, 'wts_past')
            wtb_value_past = get_bot_price_value(filtered_data, bot, 'wtb_past')

            if not wts_value or not wtb_value or not wts_value_past or not wtb_value_past:
                continue

            movement_wts = common_helper.get_movement(wts_value, wts_value_past)
            movement_wtb = common_helper.get_movement(wtb_value, wtb_value_past)
            if movement_wts > 0:
                wts_emoji = ':green_circle:'
            else:
                wts_emoji = ':red_circle:'
            if movement_wtb > 0:
                wtb_emoji = ':green_circle:'
            else:
                wtb_emoji = ':red_circle:'

            wts_value = '$' + wts_value if wts_value.isdigit() else wts_value
            wtb_value = '$' + wtb_value if wtb_value.isdigit() else wtb_value
            movement_wts = '{}{:.1f}%'.format('+' if movement_wts > 0 else '', movement_wts) if isinstance(movement_wts, float) or isinstance(movement_wts, int) else movement_wts
            movement_wtb = '{}{:.1f}%'.format('+' if movement_wtb > 0 else '', movement_wtb) if isinstance(movement_wtb, float) or isinstance(movement_wtb, int) else movement_wtb

            msg = '{}\n{} S: {} **[{}]** \n{} B: {} **[{}]**\n'.format(bot.capitalize(), wts_emoji, wts_value, movement_wts, wtb_emoji, wtb_value, movement_wtb)
            if index < math.ceil(len(filtered_data) / 3):
                stats_str += msg
            elif math.ceil(len(filtered_data) / 3) <= index < math.ceil(len(filtered_data) / 3) * 2:
                stats_str_scnd += msg
            else:
                stats_str_thrd += msg
            index += 1

        embed.add_field(name="\u200b", value=stats_str, inline=True)
        embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        embed.add_field(name="\u200b", value=stats_str_thrd, inline=True)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at
        await message.channel.send(embed=embed)
        await waiting_message.delete()
