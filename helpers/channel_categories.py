import settings
import discord


def get_channel_category(categories, category_name):
    return discord.utils.get(categories, name=category_name)


async def get_default_channel_category(guild):
    category = get_channel_category(guild.categories, settings.DEFAULT_CHANNEL_CATEGORY)
    if not category:
        return await guild.create_category(settings.DEFAULT_CHANNEL_CATEGORY)
    return category
