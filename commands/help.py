import settings
import discord
from commands.base_command import BaseCommand


class Help(BaseCommand):

    def __init__(self):
        description = "Help message"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        msg = "Hello " + message.author.mention + "!\n"

        msg += "Welcome to the MARKETPLACES MONITOR.\n\n" \
               "Thanks for using this unique tool. I am going to try to guide you with some do's and don’ts.\n" \
               "First things first, this help command, and other special commands to create channels are available only " \
               "to admins. That means, to users with roles **[{}]**.\n\n" \
               "All other guidance and info about available commands can be found by using command **{}commands**\n\n" \
               "**IMPORTANT INFO**\n" \
               "- :bangbang: don't create or delete monitor channels manually :bangbang: **Use only create/remove commands** within the bot!\n" \
               "- :bangbang: don't rename generated channels for monitor :bangbang:\n" \
               "- :bangbang: keep all channels within the created monitor channel category :bangbang:\n" \
               "- you can rename setup channel / command spam channel and the main category of monitor channels\n" \
               "- you can rearange sorting off channels manually, but keep in mind, channels need to stay within the monitor category\n" \
               "- channel creation / removing is only allowed for users with roles **[{}]**\n\n" \
               "**Hope you enjoy using marketplaces monitor.**\n\n\n" \
               "If you have any troubles, join [SUPPORT SERVER]({})!\n" \
               "".format(", ".join(settings.ALLOWED_ROLES).upper(), settings.COMMAND_PREFIX, ", ".join(settings.ALLOWED_ROLES).upper(), settings.BOT_URL, settings.BOT_URL)

        embed = discord.Embed(title="{}".format(settings.BOT_NAME), description=msg, color=settings.DEFAULT_EMBED_COLOR)

        await message.channel.send(embed=embed)
