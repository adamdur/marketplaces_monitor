import settings
import discord
import math

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Pricing(BaseCommand):

    def __init__(self):
        description = "Shows bots sorted by average price at a given time"
        params = []
        params_optional = ['days', 'type', 'renewal']
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return
        days = common_helper.get_optional_param_by_index(params_optional, 0, "1")
        type = common_helper.get_optional_param_by_index(params_optional, 1, "wtb")
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 2, "renewal")

        if not await errors_helper.check_days_param(days, message.channel):
            return
        if not await errors_helper.check_type_param(type, message.channel):
            return
        if not await errors_helper.check_renewal_param(renewal_param, message.channel):
            return

        renewal = common_helper.get_renewal_param_value(renewal_param)

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_pricing(db, type, days, renewal)

        if not await errors_helper.check_db_response(data, message.channel):
            return

        index = 1
        stats_str = ''
        stats_str_scnd = ''
        for bot in data:
            daily_count = int(bot['price'])
            if daily_count >= 5500:
                status = ':fire:'
            elif 5500 > daily_count >= 3500:
                status = ':blue_circle:'
            elif 3500 > daily_count >= 2000:
                status = ':green_circle:'
            elif 2000 > daily_count >= 1000:
                status = ':yellow_circle:'
            elif 1000 > daily_count >= 450:
                status = ':orange_circle:'
            else:
                status = ':red_circle:'
            msg = status + ' {0}. {1}\u2002|\u2002**${2:.0f}**\n'.format(index, bot['bot'].capitalize(), bot['price'])
            if index <= math.ceil(len(data) / 2):
                stats_str += msg
            else:
                stats_str_scnd += msg
            index += 1

        days_str = common_helper.get_time_string_from_days(days)

        description = "**{} bots sorted by average price of {} posts in last {}:**"
        embed = discord.Embed(title="{} {} POSTS STATS".format(renewal_param.upper(), type.upper()), description=description.format(renewal_param.upper(), type.upper(), days_str), color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="\u200b", value=stats_str, inline=True)
        embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
