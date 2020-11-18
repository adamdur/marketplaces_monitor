from commands.base_command import BaseCommand

from commands import *

import settings

COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}


async def handle_command(command, args, message, bot_client):
    if command not in COMMAND_HANDLERS:
        return

    print(f"{message.author.name}: {settings.COMMAND_PREFIX}{command} " + " ".join(args))

    cmd_obj = COMMAND_HANDLERS[command]
    try:
        req = args[:len(cmd_obj.params)]
        opt = args[len(cmd_obj.params):]
    except TypeError:
        req = []
        opt = []
    try:
        if args[0].lower() == 'help':
            msg = message.author.mention + "\nParameters required:" + " ".join(f"*<{p}>*" for p in cmd_obj.params)
            msg += "\nParameters optional:" + " ".join(f"*<{p}>*" for p in cmd_obj.params_optional)
            return await message.channel.send(msg)
    except IndexError:
        pass

    if cmd_obj.params and len(args) < len(cmd_obj.params):
        msg = message.author.mention + " Insufficient parameters!\n" \
                                       "Parameters required:" + " ".join(f"*<{p}>*" for p in cmd_obj.params)
        await message.channel.send(msg)
    else:
        await cmd_obj.handle(req, opt, message, bot_client)
