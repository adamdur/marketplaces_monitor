import settings

from commands.base_command import BaseCommand

from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Create_kw(BaseCommand):

    def __init__(self):
        description = "Create new monitor channel based on keywords"
        params = ['channel_name', 'keywords']
        params_optional = []
        guide = f'{settings.SETUP_GUIDE_URL}#heading=h.wm48wotd4lyp'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_setup_channel = await channels_helper.is_setup_channel(message)
        if not is_setup_channel:
            return

        channel_name_param = common_helper.get_param_by_index(params, 0)
        keywords = common_helper.get_param_by_index(params, 1)

        keywords_array = keywords.split(',') if keywords else []
        keywords_array = list(set(keywords_array))

        if not await errors_helper.check_channel_keywords(keywords_array, message.channel, guide=self.guide):
            return

        category = await channel_categories_helper.get_default_channel_category(message.guild)
        channel_name = channel_name_param + '-kw' if not channel_name_param.endswith('-kw') else channel_name_param
        channel = channels_helper.get_channel(message.guild.channels, channel_name)

        if channel and int(channel.category_id) == int(category.id):
            await message.channel.send(":exclamation: Channel <#{}> already exists".format(channel.id))
            return

        permissions = category.overwrites
        new_channel = await message.guild.create_text_channel(channel_name, category=category, overwrites=permissions)

        if not new_channel:
            await message.channel.send(":exclamation: Something went wrong while creating channel. Please try again")
            return

        await setup_data_helper.append_data(message.guild, 'channels', {
            new_channel.name: {
                "id": new_channel.id,
                "pings": {},
                "keywords": keywords_array
            }
        })
        await message.channel.send(":white_check_mark: Channel <#{}> created successfully".format(new_channel.id))
