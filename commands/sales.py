import settings
import discord
import os
from datetime import datetime

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper
from helpers import graph as graph_helper


class Sales(BaseCommand):

    def __init__(self):
        description = "Shows sales graph data for selected bot"
        params = ['bot']
        params_optional = []
        guide = f''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.guild.id not in settings.MACHETE_SERVER:
            return

        bot = common_helper.get_param_by_index(params, 0)

        if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
            return

        waiting_message = await message.channel.send('Gathering data, please wait...')
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_graph_sales(db, bot)

        if not await errors_helper.check_db_response(data, message.channel):
            return await waiting_message.delete()
        if not data['data']['renewal'] and not data['data']['lifetime']:
            return await waiting_message.edit(content=":exclamation: No sufficient data found for {}. Try again later...".format(bot.upper()))
        
        filepath = graph_helper.create_line_graph_sales(data, bot=bot)
        filename = filepath.rsplit('/', 1)[-1]
        file = discord.File(filepath, filename=filename)

        wts_average_all = graph_helper.get_list_average(data['data']['renewal'])
        wts_average_week = graph_helper.get_list_average(data['data']['renewal'][-7:])
        wts_average_day = round(graph_helper.get_list_average(data['data']['renewal'][-1:]), 2)
        wtb_average_all = graph_helper.get_list_average(data['data']['lifetime'])
        wtb_average_week = graph_helper.get_list_average(data['data']['lifetime'][-7:])
        wtb_average_day = round(graph_helper.get_list_average(data['data']['lifetime'][-1:]), 2)

        if not wts_average_all and not wts_average_week and not wts_average_day\
                and not wtb_average_all and not wtb_average_week and not wtb_average_day:
            return await waiting_message.edit(content=":exclamation: No sufficient data found for {}. Try again later...".format(bot.upper()))

        embed = discord.Embed(title="{}-day sales graph for {}".format(settings.GRAPH_DATA_DAYS, bot.capitalize()), description="", color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="{}-day average (Renewal):".format(settings.GRAPH_DATA_DAYS), value="${}".format(round(wts_average_all, 2)), inline=True)
        embed.add_field(name="{}-day average (Lifetime):".format(settings.GRAPH_DATA_DAYS), value="${}".format(round(wtb_average_all, 2)), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="7-day average (Renewal):", value="${}".format(round(wts_average_week, 2)), inline=True)
        embed.add_field(name="7-day average (Lifetime):", value="${}".format(round(wtb_average_week, 2)), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="24h average (Renewal):", value="{}".format(f"${wts_average_day}" if wts_average_day else 'N/A'), inline=True)
        embed.add_field(name="24h average (Lifetime):", value="{}".format(f"${wtb_average_day}" if wtb_average_day else 'N/A'), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.set_image(url="attachment://{}".format(filename))
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await message.channel.send(file=file, embed=embed)
        await waiting_message.delete()

        if os.path.exists(filepath):
            os.remove(filepath)
        return
