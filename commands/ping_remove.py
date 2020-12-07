import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Ping_remove(BaseCommand):

    def __init__(self):
        description = "Remove pings for specific channel"
        params = ['bot', 'channel_type', 'price', '@handle']
        params_optional = []
        super().__init__(description, params, params_optional)

    async def handle(self, params, params_optional, message, client):
        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        bot = common_helper.get_param_by_index(params, 0)
        type_param = common_helper.get_param_by_index(params, 1)
        price_param = common_helper.get_param_by_index(params, 2)
        handle_param = common_helper.get_param_by_index(params, 3, lower=False)
        handles = []
        for handle in handle_param.split(','):
            handles.append(handle)
        if not await errors_helper.check_bot_param(bot, message.channel):
            return
        if type_param not in ['wts', 'wtb']:
            return await message.channel.send(":x: Pings are only availabe to **[wts, wtb]** channel types.")
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
            return await setup_data_helper.remove_ping(message, channel_name, {price_param: handles})
