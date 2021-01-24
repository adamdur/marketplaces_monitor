import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Ping_add(BaseCommand):

    def __init__(self):
        description = "Create a pings for specific channel"
        params = ['bot', 'channel_type', 'price', '@handle']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.diz420gzo012'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if not is_setup_channel:
            return

        bot = common_helper.get_param_by_index(params, 0)
        type_param = common_helper.get_param_by_index(params, 1)
        price_param = common_helper.get_param_by_index(params, 2)
        handle_param = common_helper.get_param_by_index(params, 3, lower=False)
        handles = []
        for handle in handle_param.split(','):
            if handle:
                handles.append(handle)
        if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_type_param(type_param, message.channel, guide=self.guide):
            return
        if not price_param.isdigit():
            return await message.channel.send(":x: Price parameter must be a number.")
        if not handles:
            return await message.channel.send(":x: Handles parameter is required.")

        category = await channel_categories_helper.get_default_channel_category(message.guild)

        channel_name = bot + "-" + type_param
        channel = channels_helper.get_channel(message.guild.channels, channel_name)

        if not channel:
            return await message.channel.send(":exclamation: Channel **{}** not found".format(channel_name))

        if channel and int(channel.category_id) == int(category.id):
            return await setup_data_helper.add_ping(message, channel_name, {price_param: handles})
