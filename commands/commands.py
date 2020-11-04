from commands.base_command import BaseCommand


class Commands(BaseCommand):

    def __init__(self):
        description = "Displays all available commands"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        from handlers.message_handler import COMMAND_HANDLERS
        msg = message.author.mention + "\n"

        # Displays all descriptions, sorted alphabetically by command name
        for cmd in sorted(COMMAND_HANDLERS.items()):
            msg += "\n" + cmd[1].description

        await message.channel.send(msg)
