import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Create(BaseCommand):

    def __init__(self):
        description = "Create new monitor channel"
        params = ['bot', 'types']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.hbt0417dv97p'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if not is_setup_channel:
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
        permissions = category.overwrites

        for type in types:
            if not await errors_helper.check_channel_type_param(type, message.channel, guide=self.guide):
                continue

            channel_name = bot + "-" + type
            channel = channels_helper.get_channel(message.guild.channels, channel_name)

            if channel and int(channel.category_id) == int(category.id):
                await message.channel.send(":exclamation: Channel <#{}> already exists".format(channel.id))
                continue

            new_channel = await message.guild.create_text_channel(channel_name, category=category, overwrites=permissions)

            if not new_channel:
                await message.channel.send(":exclamation: Something went wrong while creating channel. Please try again")
                continue

            await setup_data_helper.append_data(message.guild, 'channels', {new_channel.name: {"id": new_channel.id, "pings": {}}})
            await message.channel.send(":white_check_mark: Channel <#{}> created successfully".format(new_channel.id))
