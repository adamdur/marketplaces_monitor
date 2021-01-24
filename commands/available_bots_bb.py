import settings
import math
import discord

from commands.base_command import BaseCommand
from helpers import setup_data as setup_data_helper


class Available_bots_bb(BaseCommand):

    def __init__(self):
        description = "List of available BotBroker bots"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        str1 = ''
        str2 = ''
        str3 = ''
        index = 1
        bots = setup_data_helper.get_botbroker_bots(pagination=True)
        total_count = bots['pagination']['total_count']
        del bots['pagination']
        for i, page in bots.items():
            for bot in page:
                name = bot['name'].replace(' ', '_')
                if 1 <= index <= math.ceil(total_count / 3):
                    str1 += '{}. {}\u2003\n'.format(index, name.lower())
                elif math.ceil(total_count / 3) < index <= math.ceil(total_count / 3) * 2:
                    str2 += '{}. {}\u2003\n'.format(index, name.lower())
                else:
                    str3 += '{}. {}\u2003\n'.format(index, name.lower())
                index += 1

        embed = discord.Embed(title="AVAILABLE BOTBROKER BOTS", description="List of available BotBroker bots:", color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="\u200b", value=str1, inline=True)
        embed.add_field(name="\u200b", value=str2, inline=True)
        embed.add_field(name="\u200b", value=str3, inline=True)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at
        await message.channel.send(embed=embed)
