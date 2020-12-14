import discord

import settings
from commands.base_command import BaseCommand

from helpers import common as common_helper


class Invite(BaseCommand):

    def __init__(self):
        description = "Generates invite link"
        params = []
        params_optional = ['permissions']
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        if message.channel.id != settings.PRIVATE_COMMANDS_CHANNEL:
            return

        permissions = common_helper.get_optional_param_by_index(params_optional, 0, "268889168")
        url = discord.utils.oauth_url(
            client_id=settings.BOT_ID,
            permissions=discord.Permissions(int(permissions))
        )

        await message.channel.send(url)
