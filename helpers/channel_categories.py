import settings
import discord

from helpers import setup_data as setup_data_helper
from helpers import channels as channels_helper


def get_channel_category(categories, category_name):
    return discord.utils.get(categories, name=category_name)


def get_channel_category_by_id(categories, category_name):
    return discord.utils.get(categories, id=category_name)


async def get_default_channel_category(guild, create=True):
    data = await setup_data_helper.get_data(guild)
    setup = data.get('setup')
    if setup.get('category'):
        category = get_channel_category_by_id(guild.categories, setup.get('category'))
    else:
        category = get_channel_category(guild.categories, settings.DEFAULT_CHANNEL_CATEGORY)

    if not category and create:
        overwrites = channels_helper.get_public_permissions_with_messages(guild)
        category = await guild.create_category(settings.DEFAULT_CHANNEL_CATEGORY, overwrites=overwrites)
    return category
