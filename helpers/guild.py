import settings
import discord

from helpers import roles as roles_helper
from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper


async def get_moderator_role(guild):
    moderator_role = roles_helper.get_role(guild.roles, settings.MODERATOR_ROLE)
    if not moderator_role:
        return await guild.create_role(name=settings.MODERATOR_ROLE)
    return moderator_role


async def base_guild_setup(guild):
    moderator_role = await get_moderator_role(guild)
    category = await channel_categories_helper.get_default_channel_category(guild)
    setup_channel = await channels_helper.get_default_setup_channel(guild, category)
    setup_data = await setup_data_helper.get_data(guild)
    return {
        str(guild.id): {
            'moderator_role': moderator_role,
            'category': category,
            'setup_channel': setup_channel,
            'setup_data': setup_data,
            'guild': guild
        }
    }
