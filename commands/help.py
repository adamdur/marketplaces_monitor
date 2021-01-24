import settings
import discord
from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from guides import setup_guides
from guides import commands_guides


class Help(BaseCommand):

    def __init__(self):
        description = "Help message"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if is_setup_channel:
            msg = setup_guides.help_message
        else:
            msg = commands_guides.help_message

        embed = discord.Embed(title="{}".format(settings.BOT_NAME), description=msg, color=settings.DEFAULT_EMBED_COLOR)
        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await message.channel.send(embed=embed)
