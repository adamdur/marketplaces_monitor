import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper


class Remove(BaseCommand):

    def __init__(self):
        description = "Remove monitor channel".format(settings.COMMAND_PREFIX, settings.COMMAND_PREFIX)
        params = ['bot', 'type']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        category = await channel_categories_helper.get_default_channel_category(message.guild)
        channel_name = params[0] + "-" + params[1]
        channel = channels_helper.get_channel(message.guild.channels, channel_name)

        if channel and channel.category_id == category.id:
            await setup_data_helper.remove_data(message.guild, 'channels', channel_name)
            await channel.delete()
            return await message.channel.send(":white_check_mark: Channel **{}** successfully deleted".format(channel_name))

        await message.channel.send(":exclamation: Channel **{}** not found".format(channel_name))
