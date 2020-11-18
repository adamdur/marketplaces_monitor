import settings
import discord
import math

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Demand(BaseCommand):

    def __init__(self):
        description = "Shows bots sorted by number of posts at a given time"
        params = []
        params_optional = ['days', 'type']
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return
        days = common_helper.get_optional_param_by_index(params_optional, 0, "1")
        type = common_helper.get_optional_param_by_index(params_optional, 1, "wtb")

        if not await errors_helper.check_days_param(days, message.channel):
            return
        if not await errors_helper.check_type_param(type, message.channel):
            return

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_posts_stats(db, type, days)

        if not await errors_helper.check_db_response(data, message.channel):
            return

        index = 1
        stats_str = ''
        stats_str_scnd = ''
        for bot in data:
            daily_count = int(bot['count']) / int(days)
            if daily_count >= 150:
                status = ':fire:'
            elif 150 > daily_count >= 90:
                status = ':green_circle:'
            elif 90 > daily_count >= 40:
                status = ':orange_circle:'
            else:
                status = ':red_circle:'
            if index <= math.ceil(len(data) / 2):
                stats_str += status + ' {0}. {1}\u2002|\u2002**{2} posts**\n'.format(index, bot['bot'].capitalize(), bot['count'])
            else:
                stats_str_scnd += status + ' {0}. {1}\u2002|\u2002**{2} posts**\n'.format(index, bot['bot'].capitalize(), bot['count'])
            index += 1

        days_str = common_helper.get_time_string_from_days(days)

        description = "**Bots sorted by number of {} posts in last {}:**"
        embed = discord.Embed(title="{} POSTS STATS".format(type.upper()), description=description.format(type.upper(), days_str), color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="\u200b", value=stats_str, inline=True)
        embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
