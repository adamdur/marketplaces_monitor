import settings


async def check_renewal_param(param, channel):
    if param.lower() not in ['renewal', 'lt']:
        await channel.send(":x: Renewal type not available. Only **[renewal, lt]** renewal types allowed")
        return False
    return True


async def check_type_param(param, channel):
    if param not in settings.ACTIVITY_CHANNEL_TYPES:
        await channel.send(":x: Channel type not available. Only **[{}]** types allowed with activity command".format(", ".join(settings.ACTIVITY_CHANNEL_TYPES)))
        return False
    return True

async def check_channel_type_param(param, channel):
    if param not in settings.ALLOWED_CHANNEL_TYPES:
        await channel.send(":x: Channel type not available. Use command **{}available_channel_types** to see list of available channel types".format(settings.COMMAND_PREFIX))
        return False
    return True


async def check_days_param(param, channel):
    if not param.isdigit() or int(param) > settings.MAX_DAYS_DATA_CAPTURE:
        await channel.send(":x: Parameter of number of days must be number with max value of **{}**".format(settings.MAX_DAYS_DATA_CAPTURE))
        return False
    return True


async def check_bot_param(param, channel):
    if param not in settings.ALLOWED_BOTS:
        await channel.send(":x: Bot not available. Use command **{}available_bots** to see list of available bots".format(settings.COMMAND_PREFIX))
        return False
    return True


async def check_db_response(data, channel):
    if not data:
        await channel.send(":exclamation: Something went wrong while calculating data. Please try again")
        return False
    return True
