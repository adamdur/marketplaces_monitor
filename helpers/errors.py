import settings
import discord

from helpers import setup_data as setup_data_helper


def error_embed(title='Error', description='Unexpected error occurred, try again.'):
    return discord.Embed(title=f':no_entry_sign: {title}', description=description, color=settings.ERROR_EMBED_COLOR)


async def check_renewal_param(param, channel):
    if param.lower() not in ['renewal', 'lt']:
        await channel.send(":x: Renewal type not available. Only **[renewal, lt]** renewal types allowed")
        return False
    return True


async def check_type_param(param, channel):
    if param not in settings.ACTIVITY_CHANNEL_TYPES:
        embed = error_embed(
            title='Unexpected channel type parameter',
            description=f'Channel type __{param}__ not available. Only **[{", ".join(settings.ACTIVITY_CHANNEL_TYPES)}]** types allowed.'
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_demand_type_param(param, channel):
    if param not in settings.DEMAND_CHANNEL_TYPES:
        embed = error_embed(
            title='Unexpected channel type parameter',
            description=f'Channel type __{param}__ not available. Only **[{", ".join(settings.DEMAND_CHANNEL_TYPES)}]** types allowed.'
        )
        await channel.send(embed=embed)
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


async def check_bb_bot_param(param, channel):
    bots = setup_data_helper.get_botbroker_bots()
    for i, page in bots.items():
        for bot in page:
            name = bot['name'].replace(' ', '_')
            if param in name.lower():
                return bot
    await channel.send(":x: Bot not found in BotBroker database. Use command **{}available_bots_bb** to see list of available bots of BotBroker".format(settings.COMMAND_PREFIX))
    return False


async def check_bb_data_type_param(param, channel):
    if param not in settings.BB_DATA_TYPES:
        await channel.send(":x: Data type not available for BotBroker. Available data types are **[{}]** for BotBroker".format(", ".join(settings.BB_DATA_TYPES)))
        return False
    return True


async def check_bb_renewal_param(param, channel):
    if param not in settings.BB_RENEWAL_TYPES:
        await channel.send(":x: Renewal type not available for BotBroker. Available renewal types are **[{}]** for BotBroker".format(", ".join(settings.BB_RENEWAL_TYPES)))
        return False
    return True
