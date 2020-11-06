import settings
import discord

from helpers import roles as roles_helper
from helpers import setup_data as setup_data_helper


def get_channel(channels, channel_name):
    return discord.utils.get(channels, name=channel_name)


def get_channel_by_id(channels, channel_id):
    return discord.utils.get(channels, id=channel_id)


def get_public_permissions(guild):
    return {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, add_reactions=False, attach_files=False, embed_links=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
    }


def get_private_permissions(guild):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
    }

    allowed_roles = roles_helper.get_allowed_roles(guild.roles)
    for allowed_role in allowed_roles:
        overwrites[allowed_role] = discord.PermissionOverwrite(read_messages=True)

    return overwrites


def get_hidden_permissions(guild):
    return {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
    }


async def get_default_setup_channel(guild, category):
    data = await setup_data_helper.get_data(guild)
    setup = data.get('setup')
    if setup.get('setup_channel'):
        channel = get_channel_by_id(guild.channels, setup.get('setup_channel'))
    else:
        channel = get_channel(guild.channels, settings.DEFAULT_SETUP_CHANNEL)

    if not channel:
        overwrites = get_private_permissions(guild)
        return await guild.create_text_channel(settings.DEFAULT_SETUP_CHANNEL, category=category, overwrites=overwrites, position=0)

    return channel


async def get_default_watcher_channel(guild, category):
    channel = get_channel(guild.channels, settings.DEFAULT_WATCHER_CHANNEL)
    if not channel:
        overwrites = get_private_permissions(guild)
        return await guild.create_text_channel(settings.DEFAULT_WATCHER_CHANNEL, category=category, overwrites=overwrites, position=0)

    return channel
