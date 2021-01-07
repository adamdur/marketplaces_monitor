import shlex

from commands_dm.base_command_dm import BaseCommandDm as BaseCommand

from commands_dm import *

import settings

COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}


async def handle_command(message, bot_client):
    # if command not in COMMAND_HANDLERS:
    #     return

    text = message.content
    print(f"DM FROM {message.author.name}: {text}")

    if text.startswith(settings.COMMAND_PREFIX) and text != settings.COMMAND_PREFIX:
        cmd_split = shlex.split(text[len(settings.COMMAND_PREFIX):])
        command = cmd_split[0].lower()
        if command in COMMAND_HANDLERS:
            cmd_obj = COMMAND_HANDLERS[command]

            try:
                req = cmd_split[1:][:len(cmd_obj.params)]
                opt = cmd_split[1:][len(cmd_obj.params):]
            except TypeError:
                req = []
                opt = []

            await cmd_obj.handle(req, opt, message, bot_client)
