import discord

import settings
from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from guides import setup_guides
from guides import commands_guides


class Guide(BaseCommand):

    def __init__(self):
        description = "Shows general guide"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if is_setup_channel:
            url = setup_guides.guide
        else:
            url = commands_guides.guide

        embed = discord.Embed(title=f"{settings.BOT_NAME} GUIDE", description=f"[SHOW GUIDE]({url})", color=settings.DEFAULT_EMBED_COLOR)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at
        return await message.channel.send(embed=embed)
