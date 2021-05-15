import settings
import discord
import math

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Ticket_stats(BaseCommand):

    def __init__(self):
        description = "Shows weekly stats of tickets in marketplaces."
        params = []
        params_optional = ['days']
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        days = common_helper.get_optional_param_by_index(params_optional, 0, '1')
        days_str = common_helper.get_time_string_from_days(days)

        if not await errors_helper.check_days_param(days, message.channel, guide=self.guide, max_days=7):
            return

        waiting_message = await message.channel.send('Gathering data, please wait...')

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_ticket_stats(db, int(days))
        embed = discord.Embed(title=f"Marketplaces ticket stats from last {days_str}", description="", color=settings.DEFAULT_EMBED_COLOR)
        idx = 1
        embed.add_field(name="\u200b", value="**Total count of tickets**", inline=False)
        for guild in data['guilds']:
            embed.add_field(name=f"{guild['guild_name']}", value=f"{guild['count']}", inline=True)
            if not idx % 2:
                embed.add_field(name="\u200b", value="\u200b", inline=True)
            idx += 1

        index = 1
        stats_str = ''
        stats_str_scnd = ''
        stats_str_thrd = ''
        stats_str_frth = ''
        for bot, count in data['bots'].items():
            if index <= 10:
                stats_str += f"> {index}. **{bot}**  |  {count}\u200b\u200b\n"
            elif 20 >= index > 10:
                stats_str_scnd += f"> {index}. **{bot}**  |  {count}\u200b\u200b\n"
            elif 30 >= index > 20:
                stats_str_thrd += f"> {index}. **{bot}**  |  {count}\u200b\u200b\n"
            elif 40 >= index > 30:
                stats_str_frth += f"> {index}. **{bot}**  |  {count}\u200b\u200b\n"
            index += 1

        embed.add_field(name="\u200b", value="**Count of tickets by bot**", inline=False)
        if stats_str:
            embed.add_field(name="\u200b", value=stats_str, inline=True)
        if stats_str_scnd:
            embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        if stats_str_thrd:
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="\u200b", value=stats_str_thrd, inline=True)
        if stats_str_frth:
            embed.add_field(name="\u200b", value=stats_str_frth, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await message.channel.send(embed=embed)
        await waiting_message.delete()
