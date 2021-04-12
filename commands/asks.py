import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Asks(BaseCommand):

    def __init__(self):
        description = "Shows last available asks for selected bot sorted by lowest price"
        params = ['bot']
        params_optional = ['renewal']
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.guild.id not in settings.MACHETE_SERVER:
            return

        bot = common_helper.get_param_by_index(params, 0)
        renewal_param = common_helper.get_optional_param_by_index(params_optional, 0, "renewal")

        if bot:
            if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
                return
            if not await errors_helper.check_renewal_param(renewal_param, message.channel, guide=self.guide):
                return
        renewal = common_helper.get_renewal_param_value(renewal_param)
        waiting_message = await message.channel.send('Gathering data, please wait...')

        db = db_helper.mysql_get_mydb()
        asks = db_helper.get_asks(db, bot, renewal)
        embed = discord.Embed(title=f"Lowest asks for {bot.upper()} {renewal_param.upper()}", description="", color=settings.DEFAULT_EMBED_COLOR)
        for ask in asks:
            embed.add_field(
                name=f"{ask['marketplace']}",
                value=f"${round(ask['price'], 0)} | <@{ask['user_id']}> | [MESSAGE]({ask['url']})",
                inline=False
            )

        embed.set_footer(text="[{}]".format(message.guild.name), icon_url=message.guild.icon_url)
        embed.timestamp = message.created_at

        await message.channel.send(embed=embed)
        await waiting_message.delete()
