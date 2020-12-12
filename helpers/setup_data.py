import json
import os
import settings

from helpers import common as common_helper


async def get_data(guild):
    file = settings.SETUP_DIR + '/' + str(guild.id) + '.json'
    if not os.path.isfile(file):
        with open(file, mode='w') as f:
            f.write(json.dumps(settings.INIT_SETUP_DATA, indent=4))
            return settings.INIT_SETUP_DATA
    else:
        with open(file) as data:
            return json.load(data)


async def get_data_by_id(guild_id):
    file = settings.SETUP_DIR + '/' + str(guild_id) + '.json'
    if not os.path.isfile(file):
        with open(file, mode='w') as f:
            f.write(json.dumps(settings.INIT_SETUP_DATA, indent=4))
            return settings.INIT_SETUP_DATA
    else:
        with open(file) as data:
            return json.load(data)


async def append_data(guild, group, value):
    if group not in settings.INIT_SETUP_DATA.keys():
        return

    data = await get_data(guild)
    key = list(value.keys())[0]
    value = list(value.values())[0]
    # if key not in data[group]:
    data[group][key] = value
    await save_data(guild, data)


async def get_guild_channels(guild):
    if 'channels' not in settings.INIT_SETUP_DATA.keys():
        return

    data = await get_data(guild)
    return data['channels']


async def get_pings_for_channel(guild, channel):
    if 'channels' not in settings.INIT_SETUP_DATA.keys():
        return

    data = await get_data(guild)
    return data['channels'][channel]['pings']


async def add_ping(message, channel, value):
    if 'channels' not in settings.INIT_SETUP_DATA.keys():
        return

    data = await get_data(message.guild)
    key = list(value.keys())[0]
    value = list(value.values())[0]
    if key not in data['channels']:
        existing_pings = data['channels'][channel]['pings']
        ping_exists = common_helper.get_dict_value_by_index(existing_pings, key)
        if ping_exists:
            handles = ping_exists + list(set(value) - set(ping_exists))
        else:
            handles = value
        data['channels'][channel]['pings'][key] = handles

        await save_data(message.guild, data)
        if handles:
            await message.channel.send(":white_check_mark: Success. Handles **{}** will be pinged in channel <#{}> at price level {}.".format(value, data['channels'][channel]['id'], key))
            return True
        else:
            await message.channel.send(":exclamation: Handle could not be created, try again...")
            return False


async def remove_ping(message, channel, value):
    if 'channels' not in settings.INIT_SETUP_DATA.keys():
        return

    data = await get_data(message.guild)
    key = list(value.keys())[0]
    value = list(value.values())[0]
    if key not in data['channels']:
        existing_pings = data['channels'][channel]['pings']
        ping_exists = common_helper.get_dict_value_by_index(existing_pings, key)
        removed = []
        ignored = []
        if ping_exists:
            handles = ping_exists
            for val in value:
                if val in handles:
                    handles.remove(val)
                    removed.append(val)
                else:
                    ignored.append(val)
        else:
            return await message.channel.send(":exclamation: No handles found for channel **{}** at price level {}".format(channel, key))
        data['channels'][channel]['pings'][key] = handles

        await save_data(message.guild, data)
        if removed:
            await message.channel.send(":white_check_mark: Success. Handles **{}** removed from channel <#{}> at price level {}.".format(removed, data['channels'][channel]['id'], key))
        if ignored:
            await message.channel.send(":exclamation: Handles **{}** not found for channel <#{}> at price level {} and were ignored.".format(ignored, data['channels'][channel]['id'], key))


async def remove_data(guild, group, value):
    if group not in settings.INIT_SETUP_DATA.keys():
        return

    data = await get_data(guild)
    if value in data[group]:
        data[group].pop(value)
        await save_data(guild, data)


async def save_data(guild, data):
    file = settings.SETUP_DIR + '/' + str(guild.id) + '.json'
    with open(file, mode='w') as f:
        f.write(json.dumps(data, indent=4))


async def delete_guild_file(guild):
    file = settings.SETUP_DIR + '/' + str(guild.id) + '.json'
    if os.path.isfile(file):
        os.remove(file)
        return True
    return False


def get_botbroker_bots(pagination=False):
    file = settings.BB_DATA_DIR + '/bots.json'
    if not os.path.isfile(file):
        with open(file, mode='w') as f:
            f.write('{}')
            return None
    else:
        with open(file) as data:
            bots = json.load(data)
            if pagination is False:
                del bots['pagination']
            return bots


def save_botbroker_bots(data):
    file = settings.BB_DATA_DIR + '/bots.json'
    with open(file, mode='w') as f:
        f.write(json.dumps(data, indent=4))
