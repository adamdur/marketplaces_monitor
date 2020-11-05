import settings

from commands.base_command import BaseCommand


class Available_channel_types(BaseCommand):

    def __init__(self):
        description = "List of available channel types to monitor"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        msg = "```\n"
        for channel in settings.ALLOWED_CHANNEL_TYPES:
            msg += channel + "\n"

        msg += "```"
        await message.channel.send(msg)
