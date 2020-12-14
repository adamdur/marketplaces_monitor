import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Remove(BaseCommand):

    def __init__(self):
        description = "Remove monitor channel"
        params = ['bot', 'types']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.s8k5iq328drd'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        bot = common_helper.get_param_by_index(params, 0)
        type_param = common_helper.get_param_by_index(params, 1)

        if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
            return

        if type_param == 'all':
            types = settings.ALLOWED_CHANNEL_TYPES
        else:
            types = type_param.split(',')

        category = await channel_categories_helper.get_default_channel_category(message.guild)
        for type in types:
            if not await errors_helper.check_channel_type_param(type, message.channel, guide=self.guide):
                continue

            channel_name = bot + "-" + type
            channel = channels_helper.get_channel(message.guild.channels, channel_name)

            if channel and channel.category_id == category.id:
                await setup_data_helper.remove_data(message.guild, 'channels', channel_name)
                await channel.delete()
                await message.channel.send(":white_check_mark: Channel **{}** successfully deleted".format(channel_name))

            if not channel and type_param != 'all':
                await message.channel.send(":exclamation: Channel **{}** not found".format(channel_name))
