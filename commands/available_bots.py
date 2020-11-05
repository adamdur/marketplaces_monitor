import settings

from commands.base_command import BaseCommand


class Available_bots(BaseCommand):

    def __init__(self):
        description = "List of available bots to monitor"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        msg = "```\n"
        for bot in settings.ALLOWED_BOTS:
            print(bot)
            msg += bot + "\n"

        print(settings.ALLOWED_BOTS['phantom'])

        msg += "```"
        await message.channel.send(msg)