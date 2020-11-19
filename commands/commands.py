import settings
from commands.base_command import BaseCommand


class Commands(BaseCommand):

    def __init__(self):
        description = "Displays all available commands"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
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
               "**<PARAM>** = required parameter\n" \
               "**[PARAM]** = optional parameter\n" \
               "*bot* - name of bot // *use command **{}available_bots** to see list of available bots*\n" \
               "*renewal* - renewal type **[renewal, lt]** / *default=renewal*\n" \
               "*types* - types of channels separated by comma. Use **all** to create all available channels. *Use command **{}available_channel_types** to see available channels*\n" \
               "*type* - single type of channel **[wts, wtb]** / *default=wtb*\n" \
               "*days* - number of days / *default=1*\n".format(settings.COMMAND_PREFIX, settings.COMMAND_PREFIX)
        msg += "\n\n" \
               "To see all parameters within specific command use:\n" \
               "**{}<command> help** - *replace <command> with your command* (e.g. **?activity help**)".format(settings.COMMAND_PREFIX)
        await message.channel.send(msg)
