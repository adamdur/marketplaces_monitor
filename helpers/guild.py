import settings
import discord

from helpers import roles as roles_helper
from helpers import channel_categories as channel_categories_helper
from helpers import channels as channels_helper
from helpers import setup_data as setup_data_helper


def get_guild(guilds, guild_name):
    return discord.utils.get(guilds, name=guild_name)


def get_guild_by_id(guilds, guild_id):
    return discord.utils.get(guilds, id=guild_id)


async def get_moderator_role(guild, create=True):
    data = await setup_data_helper.get_data(guild)
    setup = data.get('setup')
    role = False
    if setup.get('moderator_role'):
        role = roles_helper.get_role_by_id(guild.roles, setup.get('moderator_role'))
    else:
        role = roles_helper.get_role(guild.roles, settings.MODERATOR_ROLE)

    if not role and create:
        return await guild.create_role(name=settings.MODERATOR_ROLE)
    return role


async def base_guild_setup(guild):
    moderator_role = await get_moderator_role(guild)
    await setup_data_helper.append_data(guild, 'setup', {'moderator_role': moderator_role.id})
    category = await channel_categories_helper.get_default_channel_category(guild)
    await setup_data_helper.append_data(guild, 'setup', {'category': category.id})
    setup_channel = await channels_helper.get_default_setup_channel(guild, category)
    await setup_data_helper.append_data(guild, 'setup', {'setup_channel': setup_channel.id})
    commands_channel = await channels_helper.get_default_commands_channel(guild, category)
    await setup_data_helper.append_data(guild, 'setup', {'commands_channel': commands_channel.id})
    setup_data = await setup_data_helper.get_data(guild)
    return {
        str(guild.id): {
            'guild': guild,
            'moderator_role': moderator_role,
            'category': category,
            'setup_channel': setup_channel,
            'commands_channel': commands_channel,
            'setup_data': setup_data
        }
    }


async def destroy_guild(guild):
    await setup_data_helper.delete_guild_file(guild)
