import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Activity_stats(BaseCommand):

    def __init__(self):
        description = "Shows activity and average price stats for selected type and selected days"
        params = []
        params_optional = ['type', 'renewal', 'days']
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return

        type = common_helper.get_optional_param_by_index(params_optional, 0, "wtb")
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 1, "renewal")
        days = common_helper.get_optional_param_by_index(params_optional, 2, "1")

        if not await errors_helper.check_days_param(days, message.channel):
            return
        if not await errors_helper.check_type_param(type, message.channel):
            return
        if not await errors_helper.check_renewal_param(renewal_param, message.channel):
            return

        renewal = common_helper.get_renewal_param_value(renewal_param)
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_activity_stats(db, renewal, type, days)

        if not await errors_helper.check_db_response(data, message.channel):
            return

        price_list = data['price_list']
        count_list = data['count_list']
        price_list_str = ''
        count_list_str = ''
        index = 1
        idx = 1
        for price in price_list[:15]:
            price_list_str += '**{0}. {1}**\n'.format(index, price['bot'].capitalize())
            price_list_str += '> :green_circle: **\u2002+' if price['average_price_percentage'] > 0 else '> :red_circle: **\u2002'
            price_list_str += '{0:.2f}%**\u2002(${1:.0f})\n'.format(price['average_price_percentage'], price['average_price'])
            index += 1
        for count in count_list[:15]:
            count_list_str += '**{0}. {1}**\n'.format(idx, count['bot'].capitalize())
            count_list_str += '> :green_circle: **\u2002+' if count['count_percentage'] > 0 else '> :red_circle: **\u2002'
            count_list_str += '{0:.2f}%**\u2002({1:.0f} posts)\n'.format(count['count_percentage'], count['count'])
            idx += 1

        days_str = common_helper.get_time_string_from_days(days)
        description = "Data structure legend:\n" \
                      "> **[status] [movement] ([current])**\n" \
                      "> **status** = price is up :green_circle: / down :red_circle:\n" \
                      "> **movement** = percentage movement in last 24 hours compared to {} before\n" \
                      "> **current** = average price / number of posts in last 24 hours\n\n".format(days_str)
        embed = discord.Embed(title="{} BOTS {} ACTIVITY STATS".format(renewal_param.upper(), type.upper()), description=description, color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="Average price increase/decrease:\u2002\u2002", value=price_list_str, inline=True)
        embed.add_field(name="Average activity increase/decrease:", value=count_list_str, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
