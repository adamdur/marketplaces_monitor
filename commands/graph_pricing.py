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


class Graph_pricing(BaseCommand):

    def __init__(self):
        description = "Shows pricing graph data for selected bot"
        params = ['bot']
        params_optional = ['renewal']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.8wc2zffy26zy'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return

        bot = common_helper.get_param_by_index(params, 0)
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 0, "renewal")

        if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_renewal_param(renewal_param, message.channel, guide=self.guide):
            return

        renewal = common_helper.get_renewal_param_value(renewal_param)

        waiting_message = await message.channel.send('Gathering data, please wait...')
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_graph_data_pricing(db, bot, renewal)

        if not await errors_helper.check_db_response(data, message.channel):
            return await waiting_message.delete()
        if not data['wts'] and not data['wtb']:
            return await waiting_message.edit(content=":exclamation: No sufficient data found for {}. Try again later...".format(bot.upper()))
        
        filepath = graph_helper.create_line_graph(data, bot=bot, type='price')
        filename = filepath.rsplit('/', 1)[-1]
        file = discord.File(filepath, filename=filename)

        wts_average_all = graph_helper.get_list_average(data['wts'])
        wts_average_week = graph_helper.get_list_average(data['wts'][-7:])
        wts_average_day = round(data['wts_day'], 2) if data['wts_day'] else None
        wtb_average_all = graph_helper.get_list_average(data['wtb'])
        wtb_average_week = graph_helper.get_list_average(data['wtb'][-7:])
        wtb_average_day = round(data['wtb_day'], 2) if data['wtb_day'] else None

        embed = discord.Embed(title="{}-day pricing graph for {} {}".format(settings.GRAPH_DATA_DAYS, bot.capitalize(), renewal_param.lower()), description="", color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="{}-day average (WTS):".format(settings.GRAPH_DATA_DAYS), value="${}".format(round(wts_average_all, 2)), inline=True)
        embed.add_field(name="{}-day average (WTB):".format(settings.GRAPH_DATA_DAYS), value="${}".format(round(wtb_average_all, 2)), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="7-day average (WTS):", value="${}".format(round(wts_average_week, 2)), inline=True)
        embed.add_field(name="7-day average (WTB):", value="${}".format(round(wtb_average_week, 2)), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="24h average (WTS):", value="{}".format(f"${wts_average_day}" if wts_average_day else 'N/A'), inline=True)
        embed.add_field(name="24h average (WTB):", value="{}".format(f"${wtb_average_day}" if wtb_average_day else 'N/A'), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.set_image(url="attachment://{}".format(filename))
        embed.set_footer(text="[{}]".format(settings.BOT_NAME), icon_url=settings.BOT_ICON)
        embed.timestamp = datetime.now()

        await message.channel.send(file=file, embed=embed)
        await waiting_message.delete()

        if os.path.exists(filepath):
            os.remove(filepath)
        return
