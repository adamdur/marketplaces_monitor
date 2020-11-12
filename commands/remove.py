import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper


class Remove(BaseCommand):

    def __init__(self):
        description = "Remove monitor channel"
                      # "```bot = name of bot // use command '{}available_bots' to see list of available bots\n" \
                      # "types = types of channels separated by comma. Use 'all' to delete all channels related to bot\n" \
                      # "use command '{}available_channel_types' to see list of available channel types```".format(settings.COMMAND_PREFIX, settings.COMMAND_PREFIX)
        params = ['bot', 'types']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        if params[0] not in settings.ALLOWED_BOTS:
            return await message.channel.send(":x: Bot not available. Use command **{}available_bots** to see list of available bots".format(settings.COMMAND_PREFIX))

        if params[1] == 'all':
            types = settings.ALLOWED_CHANNEL_TYPES
        else:
            types = params[1].split(',')

        category = await channel_categories_helper.get_default_channel_category(message.guild)
        for type in types:
            if type not in settings.ALLOWED_CHANNEL_TYPES:
                await message.channel.send(":x: Channel type not available. Use command **{}available_channel_types** to see list of available channel types".format(settings.COMMAND_PREFIX))
                continue

            channel_name = params[0] + "-" + type
            channel = channels_helper.get_channel(message.guild.channels, channel_name)

            if channel and channel.category_id == category.id:
                await setup_data_helper.remove_data(message.guild, 'channels', channel_name)
                await channel.delete()
                await message.channel.send(":white_check_mark: Channel **{}** successfully deleted".format(channel_name))

            if not channel and params[1] != 'all':
                await message.channel.send(":exclamation: Channel **{}** not found".format(channel_name))
