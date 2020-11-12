import settings
from commands.base_command import BaseCommand


class Commands(BaseCommand):

    def __init__(self):
        description = "Displays all available commands"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        from handlers.message_handler import COMMAND_HANDLERS
        msg = message.author.mention + "\n"

        for cmd in sorted(COMMAND_HANDLERS.items()):
            if cmd[1].name.lower() not in settings.PRIVATE_COMMANDS:
                if cmd[1].name.lower() in settings.ADMIN_COMMANDS:
                    if [role for role in message.author.roles if role.name.lower() in settings.ALLOWED_ROLES]:
                        msg += cmd[1].description
                else:
                    msg += cmd[1].description

        msg += "\n\n" \
               ">>> **PARAMETERS DESCRIPTION:**\n" \
               "*<bot>* - name of bot // *use command **{}available_bots** to see list of available bots*\n" \
               "*<renewal_type>* - renewal type **[renewal, lt]**\n" \
               "*<types>* - types of channels separated by comma. Use **all** to create all available channels // *use command **{}available_channel_types** to see available channels*\n" \
               "*<type>* - single type of channel **[wts, wtb]**\n" \
               "*<days>* - number of days\n".format(settings.COMMAND_PREFIX, settings.COMMAND_PREFIX)

        await message.channel.send(msg)
