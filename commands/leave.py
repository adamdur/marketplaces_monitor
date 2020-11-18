import discord

import settings
from commands.base_command import BaseCommand


class Leave(BaseCommand):

    def __init__(self):
        description = "Leave specific guild"
        params = ['guild_id']
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        if message.channel.id != settings.PRIVATE_COMMANDS_CHANNEL:
            return

        guild_id = params[0]

        guild = discord.utils.get(client.guilds, id=int(guild_id))
        if guild is None:
            await message.channel.send("No guild found sorry")
            return
        await message.channel.send("guild found, leaving bye bye")
        await guild.leave()
