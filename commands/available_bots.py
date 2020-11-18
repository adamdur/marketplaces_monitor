import settings
import math
import discord

from commands.base_command import BaseCommand


class Available_bots(BaseCommand):

    def __init__(self):
        description = "List of available bots to monitor"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        str1 = ''
        str2 = ''
        str3 = ''
        index = 1
        for bot in settings.ALLOWED_BOTS:
            if 1 <= index <= math.ceil(len(settings.ALLOWED_BOTS) / 3):
                str1 += '{}. {}\u2003\n'.format(index, bot)
            elif math.ceil(len(settings.ALLOWED_BOTS) / 3) < index <= math.ceil(len(settings.ALLOWED_BOTS) / 3) * 2:
                str2 += '{}. {}\u2003\n'.format(index, bot)
            else:
                str3 += '{}. {}\u2003\n'.format(index, bot)
            index += 1

        embed = discord.Embed(title="AVAILABLE BOTS", description="List of available bots:", color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="\u200b", value=str1, inline=True)
        embed.add_field(name="\u200b", value=str2, inline=True)
        embed.add_field(name="\u200b", value=str3, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
