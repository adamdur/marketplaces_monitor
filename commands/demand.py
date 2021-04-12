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
        params_optional = ['channel_type', 'days']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.su070w5nhnc9'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        type = common_helper.get_optional_param_by_index(params_optional, 0, "wtb")
        days = common_helper.get_optional_param_by_index(params_optional, 1, "1")

        if not await errors_helper.check_days_param(days, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_demand_type_param(type, message.channel, guide=self.guide):
            return

        waiting_message = await message.channel.send('Gathering data, please wait...')
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_posts_stats(db, type, days)

        if not await errors_helper.check_db_response(data, message.channel):
            return await waiting_message.delete()

        MAX = 70
        MID = 35
        MIN = 15
        if type in ['wtr', 'wtro']:
            MAX = 55
            MID = 25
            MIN = 10

        index = 1
        stats_str = ''
        stats_str_scnd = ''
        stats_str_thrd = ''
        stats_str_frth = ''
        for bot in data:
            daily_count = int(bot['unique_users']) / int(days)
            if daily_count >= MAX:
                status = ':fire:'
            elif MAX > daily_count >= MID:
                status = ':green_circle:'
            elif MID > daily_count >= MIN:
                status = ':orange_circle:'
            else:
                status = ':red_circle:'
            msg = status + f" **{index}. {bot['bot'].capitalize()}\u2002|\u2002{bot['unique_users']} users**\n> {bot['count']} total posts\n"
            if index <= math.ceil(len(data) / 4):
                stats_str += msg
            elif math.ceil(len(data) / 4) <= index <= math.ceil(len(data) / 4) * 2:
                stats_str_scnd += msg
            elif math.ceil(len(data) / 4) <= index <= math.ceil(len(data) / 4) * 3:
                stats_str_thrd += msg
            else:
                stats_str_frth += msg
            index += 1

        days_str = common_helper.get_time_string_from_days(days)

        description = "**Bots sorted by number of {} posts in last {}:**"
        embed = discord.Embed(title="{} POSTS STATS".format(type.upper()), description=description.format(type.upper(), days_str), color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="\u200b", value=stats_str, inline=True)
        embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="\u200b", value=stats_str_thrd, inline=True)
        embed.add_field(name="\u200b", value=stats_str_frth, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at
        await message.channel.send(embed=embed)
        await waiting_message.delete()
