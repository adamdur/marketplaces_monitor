import json
import os
import settings


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
    if key not in data[group]:
        data[group][key] = value
        await save_data(guild, data)


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