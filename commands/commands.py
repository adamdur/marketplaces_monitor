import discord
import settings
from commands.base_command import BaseCommand

from helpers import channels as channels_helper


class Commands(BaseCommand):

    def __init__(self):
        description = "Displays all available commands"
        params = []
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        from handlers.message_handler import COMMAND_HANDLERS
        is_setup_channel = await channels_helper.is_setup_channel(message)
        is_command_channel = await channels_helper.is_commands_channel(message)
        embed = discord.Embed(title="List of available commands", description="", color=settings.DEFAULT_EMBED_COLOR)
        if is_setup_channel:
            embed = build_embed(embed, COMMAND_HANDLERS, 'setup')
        elif is_command_channel:
            embed = build_embed(embed, COMMAND_HANDLERS, 'command')

        embed.add_field(name="\u200b", value="**HELP COMMANDS**", inline=False)
        embed.add_field(name=f"{settings.COMMAND_PREFIX}help", value='Shows help message', inline=False)
        embed.add_field(name=f"{settings.COMMAND_PREFIX}guide", value='Shows general guide', inline=False)
        embed.add_field(name=f"{settings.COMMAND_PREFIX}commands", value='Shows available commands', inline=False)

        await message.channel.send(embed=embed)


def build_embed(embed, handlers, ctype):
    for cmd in sorted(handlers.items()):
        if cmd[1].name.lower() not in settings.PRIVATE_COMMANDS:
            if ctype == 'setup':
                if cmd[1].name.lower() in settings.ADMIN_COMMANDS and cmd[1].name.lower() not in settings.COMMON_COMMANDS:
                    command = "**{}{}**".format(settings.COMMAND_PREFIX, cmd[1].name)
                    if cmd[1].params:
                        command += " " + " ".join(f"*<{p}>*" for p in cmd[1].params)
                    if cmd[1].params_optional:
                        command += " " + " ".join(f"*[{p}]*" for p in cmd[1].params_optional)
                    embed.add_field(name=command, value=cmd[1].description, inline=False)
            elif ctype == 'command':
                if cmd[1].name.lower() not in settings.ADMIN_COMMANDS and cmd[1].name.lower() not in settings.COMMON_COMMANDS:
                    command = "**{}{}**".format(settings.COMMAND_PREFIX, cmd[1].name)
                    if cmd[1].params:
                        command += " " + " ".join(f"*<{p}>*" for p in cmd[1].params)
                    if cmd[1].params_optional:
                        command += " " + " ".join(f"*[{p}]*" for p in cmd[1].params_optional)
                    embed.add_field(name=command, value=cmd[1].description, inline=False)
    return embed
