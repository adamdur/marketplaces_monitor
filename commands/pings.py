import settings
import discord

from commands.base_command import BaseCommand

from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Pings(BaseCommand):

    def __init__(self):
        description = "Shows pings for specific channel"
        params = ['bot']
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        bot = common_helper.get_param_by_index(params, 0)
        if not await errors_helper.check_bot_param(bot, message.channel):
            return

        channels = await setup_data_helper.get_guild_channels(message.guild)
        embed = discord.Embed(title="PINGS FOR {}".format(bot.upper()), description="", color=settings.DEFAULT_EMBED_COLOR)

        for channel, channel_data in channels.items():
            bot_name, channel_type = channel.split('-')
            if bot_name == bot and channel_type in ['wts', 'wtb']:
                channel_pings = channel_data['pings']
                if channel_pings:
                    title_added = False
                    for price, handles in channel_pings.items():
                        if handles:
                            if not title_added:
                                embed.add_field(name="\u200b", value="> #{}".format(channel), inline=False)
                                title_added = True
                            embed.add_field(name="Price level: {}".format(price), value="Handles: {}".format((", ").join(handles)), inline=False)
        if embed.fields:
            return await message.channel.send(embed=embed)
        else:
            embed.add_field(name="\u200b", value=":x: No ping handles found for {}.".format(bot), inline=False)
            return await message.channel.send(embed=embed)
