import settings
import discord

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import guild as guild_helper


class Leave(BaseCommand):

    def __init__(self):
        description = "Leave specific guild"
        params = ['guild_id']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if message.channel.id != settings.PRIVATE_COMMANDS_CHANNEL:
            return

        guild_id = params[0]

        guild = discord.utils.get(client.guilds, id=int(guild_id))
        if guild is None:
            await message.channel.send("No guild found sorry")
            return
        await message.channel.send("guild found, leaving bye bye")
        await guild.leave()
