import settings
import math
import discord

from commands.base_command import BaseCommand


class Available_channel_types(BaseCommand):

    def __init__(self):
        description = "List of available channel types to monitor"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        str1 = ''
        index = 1
        for type in settings.ALLOWED_CHANNEL_TYPES:
            str1 += '{}. {}\u2003\n'.format(index, type)
            index += 1

        embed = discord.Embed(title="AVAILABLE CHANNEL TYPES", description="List of available channel types to monitor:", color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="\u200b", value=str1, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
