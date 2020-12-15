import settings
import discord

from helpers import setup_data as setup_data_helper


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


async def check_days_param(param, channel, guide=None):
    if not param.isdigit() or int(param) > settings.MAX_DAYS_DATA_CAPTURE:
        embed = error_embed(
            title='Invalid days parameter',
            description=f'Parameter of number of days must be number with max value of **{settings.MAX_DAYS_DATA_CAPTURE}**.',
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
