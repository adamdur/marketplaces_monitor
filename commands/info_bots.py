import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Info_bots(BaseCommand):

    def __init__(self):
        description = "Shows available info bots"
        params = []
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if not message.guild.id == settings.MACHETE_SERVER:
            return

        bot_data = await errors_helper.check_info_bot(False, message.channel, guide=self.guide)
        if not bot_data:
            return

        embed = discord.Embed(
            title=f"LIST OF AVAILABLE BOT GUIDES",
            description="",
            color=settings.DEFAULT_EMBED_COLOR
        )
        i = 1
        bot_str = ""
        for bot in bot_data:
            bot_str += f"{i}. {bot['bot']} \n"
            i += 1
        embed.add_field(name="\u200b", value=f"{bot_str}", inline=False)
        embed.set_footer(text=f"{message.guild.name}", icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await message.channel.send(embed=embed)
