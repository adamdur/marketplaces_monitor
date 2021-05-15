import settings
import discord

from helpers import setup_data as setup_data_helper
from helpers import db as db_helper


def error_embed(title='Unexpected error', description='Unexpected error occurred, try again.', guide=None):
    description += "\n\n>>> Try **.<command> help** to see help for specific command\n*(replace **<command>** with your command name)*"
    embed = discord.Embed(title=f':no_entry_sign: {title} :no_entry_sign:', description=description, color=settings.ERROR_EMBED_COLOR)
    if (guide):
        embed.add_field(name="\u200b", value=f"[SHOW GUIDE]({guide})", inline=False)
    else:
        embed.add_field(name="\u200b", value=f"Show general guide by using command: **{settings.COMMAND_PREFIX}guide**", inline=False)
    return embed


def no_data_embed(title='No sufficient data!', description='Sorry, at this time, no sufficient data were found, try again later.'):
    return discord.Embed(title=f':hourglass_flowing_sand: {title} :hourglass_flowing_sand:', description=description, color=settings.ERROR_EMBED_COLOR)


async def check_renewal_param(param, channel, guide=None):
    if param.lower() not in ['renewal', 'lt', 'lifetime']:
        embed = error_embed(
            title='Unexpected renewal type parameter',
            description=f"Renewal type __{param}__ not available. Only **['renewal', 'lifetime']** types allowed.",
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_type_param(param, channel, guide=None):
    if param not in settings.ACTIVITY_CHANNEL_TYPES:
        embed = error_embed(
            title='Unexpected channel type parameter',
            description=f'Channel type __{param}__ not available. Only **[{", ".join(settings.ACTIVITY_CHANNEL_TYPES)}]** types allowed.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_timeframe_param(param, channel, guide=None):
    if param not in ['d', 'w', 'm']:
        embed = error_embed(
            title='Unexpected timeframe parameter',
            description=f"Timeframe __{param}__ not available. Only **[{', '.join(['d', 'w', 'm'])}]** types allowed.\n"
                        f"d = day, w = week, m = month",
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_demand_type_param(param, channel, guide=None):
    if param not in settings.DEMAND_CHANNEL_TYPES:
        embed = error_embed(
            title='Unexpected channel type parameter',
            description=f'Channel type __{param}__ not available. Only **[{", ".join(settings.DEMAND_CHANNEL_TYPES)}]** types allowed.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_channel_type_param(param, channel, guide=None):
    if param not in settings.ALLOWED_CHANNEL_TYPES:
        embed = error_embed(
            title='Unexpected channel type parameter',
            description=f'Channel type __{param}__ not available. Use command **{settings.COMMAND_PREFIX}available_channel_types** to see list of available channel types.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_days_param(param, channel, guide=None, max_days=settings.MAX_DAYS_DATA_CAPTURE):
    if not param.isdigit() or int(param) > max_days:
        embed = error_embed(
            title='Invalid days parameter',
            description=f'Parameter of number of days must be number with max value of **{max_days}**.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_bot_param(param, channel, guide=None):
    if param not in settings.ALLOWED_BOTS:
        embed = error_embed(
            title='Unexpected bot name parameter',
            description=f'Bot __{param}__ not available. Use command **{settings.COMMAND_PREFIX}available_bots** to see list of available bots.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_channel_keywords(keywords_array, channel, guide=None):
    keywords = keywords_array
    length = len(keywords)
    if length < 2:
        embed = error_embed(
            title='Insufficient number of main keywords',
            description=f'You have {length} main keywords. Please add at least 2 main keywords',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    if length > 5:
        embed = error_embed(
            title='Exceeded max number of main keywords',
            description=f'Max number of main keywords is 5. Your number of main keywords is {length}.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False

    for keyword in keywords:
        kw_options = keyword.split('|')
        if len(kw_options) > 5:
            embed = error_embed(
                title='Exceeded max number of keyword aliases',
                description=f'Max number of keyword aliases is 5. Aliases in **{kw_options}** exceed this limit',
                guide=guide
            )
            await channel.send(embed=embed)
            return False
    return True


async def check_db_response(data, channel, guide=None):
    if not data:
        embed = error_embed(guide=guide)
        await channel.send(embed=embed)
        return False
    return True


async def check_bb_bot_param(param, channel, guide=None):
    bots = setup_data_helper.get_botbroker_bots()
    for i, page in bots.items():
        for bot in page:
            name = bot['name'].replace(' ', '_')
            if param in name.lower():
                return bot
    embed = error_embed(
        title='Unexpected bot parameter',
        description=f'Bot __{param}__ not available for BotBroker. Use command **{settings.COMMAND_PREFIX}available_bots_bb** to see list of available bots of BotBroker.',
        guide=guide
    )
    await channel.send(embed=embed)
    return False


async def check_bb_data_type_param(param, channel, guide=None):
    if param not in settings.BB_DATA_TYPES:
        embed = error_embed(
            title='Unexpected data type parameter',
            description=f'Data type __{param}__ not available for BotBroker. Available data types are **[{", ".join(settings.BB_DATA_TYPES)}]** for BotBroker.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_bb_renewal_param(param, channel, guide=None):
    if param not in settings.BB_RENEWAL_TYPES:
        embed = error_embed(
            title='Unexpected renewal type parameter',
            description=f'Renewal type __{param}__ not available for BotBroker. Available renewal types are **[{", ".join(settings.BB_RENEWAL_TYPES)}]** for BotBroker.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return True


async def check_info_bot(param, channel, guide=None):
    db = db_helper.mysql_get_mydb()
    bot_exists = db_helper.get_info_bots(db, param)
    if not bot_exists:
        embed = error_embed(
            title='Bot guide not found',
            description=f'Use command **{settings.COMMAND_PREFIX}info_bots** to see available bot guides.',
            guide=guide
        )
        await channel.send(embed=embed)
        return False
    return bot_exists
