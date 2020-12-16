import settings
import discord

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Keywords(BaseCommand):

    def __init__(self):
        description = "Check keywords for monitor channel"
        params = ['channel_name']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.pqktm26avpnd'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if not is_setup_channel:
            return

        channel_name_param = common_helper.get_param_by_index(params, 0)

        category = await channel_categories_helper.get_default_channel_category(message.guild)
        channel_name = channel_name_param + '-kw' if not channel_name_param.endswith('-kw') else channel_name_param
        channel = channels_helper.get_channel(message.guild.channels, channel_name)

        if not channel:
            error_embed = errors_helper.error_embed(
                title=f'Channel not found',
                description=f'Channel #{channel_name} not found',
                guide=self.guide
            )
            return await message.channel.send(embed=error_embed)

        if channel and int(channel.category_id) == int(category.id):
            data = await setup_data_helper.get_guild_channels(message.guild)
            keywords = []
            try:
                keywords = data[channel_name]['keywords']
            except KeyError:
                error_embed = errors_helper.error_embed(
                    title=f'No keywords data',
                    description=f'No keywords data found for channel #{channel_name}',
                    guide=self.guide
                )
                return await message.channel.send(embed=error_embed)

            if keywords:
                embed = discord.Embed(
                    title=f'CHANNEL KEYWORDS CHECKER',
                    description=f'List of keywords for channel #{channel_name}\n'
                                f'> At least one of the keyword from each group must be matched.',
                    color=settings.DEFAULT_EMBED_COLOR
                )
                index = 1
                for keyword in keywords:
                    kw_options = keyword.split('|')
                    embed.add_field(name=f'Keyword group {index}', value=f'[{",".join(kw_options)}]', inline=False)
                    index += 1
                await message.channel.send(embed=embed)
