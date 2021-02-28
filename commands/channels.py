import settings
import discord

from commands.base_command import BaseCommand

from helpers import common as common_helper
from helpers import errors as errors_helper
from helpers import db as db_helper


class Channels(BaseCommand):

    def __init__(self):
        description = "Provides links to marketplaces channels"
        params = ['bot']
        params_optional = ['type']
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.guild.id not in settings.MACHETE_SERVER:
            return

        bot = common_helper.get_param_by_index(params, 0)
        type_param = common_helper.get_optional_param_by_index(params_optional, 0)

        try:
            db = db_helper.mysql_get_mydb()
            channels = db_helper.get_channels(db, bot, type_param)
        except:
            embed = errors_helper.error_embed()
            await message.channel.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"MARKETPLACES CHANNELS FOR {bot.upper()}{' ' + type_param.upper() if type_param else ''}",
            description="",
            color=settings.DEFAULT_EMBED_COLOR
        )
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        if not channels:
            embed.add_field(name=f"No channels found for {bot.upper()}", value=f"\u200b", inline=False)
            return await message.channel.send(embed=embed)

        data = {}
        for channel in channels:
            guild_index = ''
            if channel['guild_name'] == 'botmart':
                guild_index = '1'
            elif channel['guild_name'] == 'tidal_market_place':
                guild_index = '2'
            elif channel['guild_name'] == 'splash_market':
                guild_index = '3'
            elif channel['guild_name'] == 'didi_market':
                guild_index = '4'
            elif channel['guild_name'] == 'tiger_zone':
                guild_index = '5'

            channel_index = ''
            if channel['type'] == 'wts':
                channel_index = '1'
            elif channel['type'] == 'wtb':
                channel_index = '2'
            elif channel['type'] == 'wtro':
                channel_index = '3'
            elif channel['type'] == 'wtr':
                channel_index = '4'

            try:
                data[guild_index]['channels'][channel_index] = f"{channel['type']}||{channel['url']}"
            except KeyError:
                data[guild_index] = {
                    'name': channel['guild_name'],
                    'channels': {
                        channel_index: f"{channel['type']}||{channel['url']}"
                    }
                }
        for server in sorted(data):
            channels_str = ''
            idx = 1
            for channel in sorted(data[server]['channels']):
                channel_values = data[server]['channels'][channel].split("||")
                channels_str += f"[{channel_values[0].upper()}]({channel_values[1]})"
                if idx < len(data[server]['channels']):
                    channels_str += "\u2002|\u2002"
                idx += 1
            embed.add_field(name=f"{data[server]['name'].replace('_', ' ').capitalize()}", value=f"{channels_str}", inline=False)

        await message.channel.send(embed=embed)
