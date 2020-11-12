import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper


class Create(BaseCommand):

    def __init__(self):
        description = "Create new monitor channel"
        params = ['bot', 'types']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if not is_setup_channel:
            return

        if message.channel.name.lower() != settings.DEFAULT_SETUP_CHANNEL:
            return

        if params[0] not in settings.ALLOWED_BOTS:
            return await message.channel.send(":x: Bot not available. Use command **{}available_bots** to see list "
                                              "of available bots".format(settings.COMMAND_PREFIX))

        if params[1] == 'all':
            types = settings.ALLOWED_CHANNEL_TYPES
        else:
            types = params[1].split(',')

        for type in types:
            if type not in settings.ALLOWED_CHANNEL_TYPES:
                await message.channel.send(":x: Channel type not available. Use command **{}available_channel_types** "
                                           "to see list of available channel types".format(settings.COMMAND_PREFIX))
                continue

            category = await channel_categories_helper.get_default_channel_category(message.guild)
            channel_name = params[0] + "-" + type
            channel = channels_helper.get_channel(message.guild.channels, channel_name)

            if channel and int(channel.category_id) == int(category.id):
                await message.channel.send(":exclamation: Channel <#{}> already exists".format(channel.id))
                continue

            overwrites = channels_helper.get_public_permissions(message.guild)
            new_channel = await message.guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

            if not new_channel:
                await message.channel.send(":exclamation: Something went wrong while creating channel. Please try again")
                continue

            await setup_data_helper.append_data(message.guild, 'channels', {new_channel.name: new_channel.id})
            await message.channel.send(":white_check_mark: Channel <#{}> created successfully".format(new_channel.id))
