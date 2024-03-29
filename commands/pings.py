import settings
import discord

from commands.base_command import BaseCommand

from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper
from helpers import channels as channels_helper


class Pings(BaseCommand):

    def __init__(self):
        description = "Shows pings for specific channel"
        params = ['bot']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.fd6wtvry8lmr'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if not is_setup_channel:
            return

        bot = common_helper.get_param_by_index(params, 0)
        if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
            return

        channels = await setup_data_helper.get_guild_channels(message.guild)
        embed = discord.Embed(title="PINGS FOR {}".format(bot.upper()), description="", color=settings.DEFAULT_EMBED_COLOR)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        for channel, channel_data in channels.items():
            if len(channel.split('-')) > 2:
                continue
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
