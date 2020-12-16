import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper


class Remove_kw(BaseCommand):

    def __init__(self):
        description = "Remove keyword monitor channel"
        params = ['channel_name']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.98noja5bs7xq'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        channel_name_param = common_helper.get_param_by_index(params, 0)

        category = await channel_categories_helper.get_default_channel_category(message.guild)

        channel_name = channel_name_param + '-kw' if not channel_name_param.endswith('-kw') else channel_name_param
        channel = channels_helper.get_channel(message.guild.channels, channel_name)

        if channel and channel.category_id == category.id:
            await setup_data_helper.remove_data(message.guild, 'channels', channel_name)
            await channel.delete()
            await message.channel.send(":white_check_mark: Channel **{}** successfully deleted".format(channel_name))

        if not channel:
            await message.channel.send(":exclamation: Channel **{}** not found".format(channel_name))
