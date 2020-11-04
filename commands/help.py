from commands.base_command import BaseCommand


class Help(BaseCommand):

    def __init__(self):
        description = "Help command for more in depth guide"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        msg = "```" \
              "This is line 1 \n" \
              "This is line 2" \
              "```"

        await message.channel.send(msg)
