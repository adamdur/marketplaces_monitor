import discord
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
        embed = discord.Embed(title="List of available commands", description=message.author.mention, color=settings.DEFAULT_EMBED_COLOR)
        for cmd in sorted(COMMAND_HANDLERS.items()):
            if cmd[1].name.lower() not in settings.PRIVATE_COMMANDS:
                if cmd[1].name.lower() in settings.ADMIN_COMMANDS:
                    if [role for role in message.author.roles if role.name.lower() in settings.ALLOWED_ROLES]:
                        command = "**{}{}**".format(settings.COMMAND_PREFIX, cmd[1].name)
                        if cmd[1].params:
                            command += " " + " ".join(f"*<{p}>*" for p in cmd[1].params)
                        if cmd[1].params_optional:
                            command += " " + " ".join(f"*[{p}]*" for p in cmd[1].params_optional)
                        embed.add_field(name=command, value=cmd[1].description, inline=False)
                else:
                    command = "**{}{}**".format(settings.COMMAND_PREFIX, cmd[1].name)
                    if cmd[1].params:
                        command += " " + " ".join(f"*<{p}>*" for p in cmd[1].params)
                    if cmd[1].params_optional:
                        command += " " + " ".join(f"*[{p}]*" for p in cmd[1].params_optional)
                    embed.add_field(name=command, value=cmd[1].description, inline=False)

        msg = ">>> **PARAMETERS DESCRIPTION:**\n" \
               "**<PARAM>** = required parameter\n" \
               "**[PARAM]** = optional parameter\n" \
               "*bot* - name of bot // *use command **{}available_bots** to see list of available bots*\n" \
               "*renewal* - renewal type **[renewal, lt]** / *default=renewal*\n" \
               "*types* - types of channels separated by comma. Use **all** to create all available channels. *Use command **{}available_channel_types** to see available channels*\n" \
               "*type* - single type of channel **[wts, wtb]** / *default=wtb*\n" \
               "*days* - number of days / *default=1*\n".format(settings.COMMAND_PREFIX, settings.COMMAND_PREFIX)
        msg += "\n\n" \
               "To see all parameters within specific command use:\n" \
               "**{}<command> help** - *replace <command> with your command* (e.g. **{}activity help**)".format(settings.COMMAND_PREFIX, settings.COMMAND_PREFIX)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Useful info", value=msg, inline=False)
        await message.channel.send(embed=embed)
