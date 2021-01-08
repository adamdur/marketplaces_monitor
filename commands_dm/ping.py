import settings
import discord

from commands_dm.base_command_dm import BaseCommandDm as BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Ping(BaseCommand):

    def __init__(self):
        description = "Ping"
        params = []
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        await message.author.send("Pong. I'm listening.")
