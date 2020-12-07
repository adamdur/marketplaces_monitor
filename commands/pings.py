import settings
import discord

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Pings(BaseCommand):

    def __init__(self):
        description = "Shows pings for specific channel"
        params = ['bot', 'channel_type']
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        bot = common_helper.get_param_by_index(params, 0)
        type_param = common_helper.get_param_by_index(params, 1)
        if not await errors_helper.check_bot_param(bot, message.channel):
            return
        if type_param not in ['wts', 'wtb']:
            return await message.channel.send(":x: Pings are only available to **[wts, wtb]** channel types.")

        category = await channel_categories_helper.get_default_channel_category(message.guild)

        channel_name = bot + "-" + type_param
        channel = channels_helper.get_channel(message.guild.channels, channel_name)

        if not channel:
            return await message.channel.send(":exclamation: Channel **{}** not found".format(channel_name))

        if channel and int(channel.category_id) == int(category.id):
            pings = await setup_data_helper.get_pings(message.guild, channel_name)
            embed = discord.Embed(title="PINGS FOR CHANNEL #{}".format(channel_name), description="", color=settings.DEFAULT_EMBED_COLOR)

            for price, handles in pings.items():
                if handles:
                    embed.add_field(name="Price level: {}".format(price), value="Handles: {}".format((", ").join(handles)), inline=False)
            if embed.fields:
                return await message.channel.send(embed=embed)
            else:
                embed.add_field(name="\u200b", value=":x: No ping handles found.", inline=False)
                return await message.channel.send(embed=embed)
