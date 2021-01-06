import discord
from datetime import datetime

from commands.base_command import BaseCommand
from helpers import db as db_helper

from commands import *

import settings

COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}


async def handle_command(command, args, message, bot_client):
    if command not in COMMAND_HANDLERS:
        return

    print(f"{message.author.name}: {settings.COMMAND_PREFIX}{command} " + " ".join(args))
    log_data = (
        f"{settings.COMMAND_PREFIX}{command}",
        f" ".join(args),
        f"{message.guild.name}",
        f"{message.guild.id}",
        f"{message.author.name}#{message.author.discriminator}",
        f"{message.author.id}",
        datetime.now(),
    )

    cmd_obj = COMMAND_HANDLERS[command]
    try:
        req = args[:len(cmd_obj.params)]
        opt = args[len(cmd_obj.params):]
    except TypeError:
        req = []
        opt = []
    try:
        if args[0].lower() == 'help':
            if cmd_obj.params or cmd_obj.params_optional:
                embed = discord.Embed(title=f"{cmd_obj.name.upper()} COMMAND PARAMETERS OVERVIEW", description="", color=settings.DEFAULT_EMBED_COLOR)
                embed.add_field(name=f"{settings.COMMAND_PREFIX}{cmd_obj.name} " + " ".join(f"*<{p}>*" for p in cmd_obj.params) + " " + " ".join(f"*[{p}]*" for p in cmd_obj.params_optional), value="\u200b", inline=False)
                if cmd_obj.params:
                    embed.add_field(name="Parameters required:", value=" ".join(f"*<{p}>*" for p in cmd_obj.params), inline=False)
                if cmd_obj.params_optional:
                    embed.add_field(name="Parameters optional:", value=" ".join(f"*<{p}>*" for p in cmd_obj.params_optional), inline=False)
                await message.channel.send(embed=embed)
                return log_cmd(log_data)
        if args[0].lower() == 'guide':
            if not cmd_obj.guide:
                embed = discord.Embed(title=f"{cmd_obj.name.upper()} COMMAND GUIDE", description="Sorry, guide for selected command not available.", color=settings.DEFAULT_EMBED_COLOR)
                await message.channel.send(embed=embed)
                return log_cmd(log_data)
            embed = discord.Embed(title=f"{cmd_obj.name.upper()} COMMAND GUIDE", description=f"[SHOW GUIDE]({cmd_obj.guide})", color=settings.DEFAULT_EMBED_COLOR)
            await message.channel.send(embed=embed)
            return log_cmd(log_data)
    except IndexError:
        pass

    if cmd_obj.params and len(args) < len(cmd_obj.params):
        msg = message.author.mention + " Insufficient parameters!\n" \
                                       "Parameters required:" + " ".join(f"*<{p}>*" for p in cmd_obj.params)
        await message.channel.send(msg)
    else:
        await cmd_obj.handle(req, opt, message, bot_client)
    log_cmd(log_data)


def log_cmd(data):
    db = db_helper.mysql_get_mydb()
    db_helper.log_command(db, data)
