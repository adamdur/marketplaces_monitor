import sys
import time
import re

from discord.ext.commands import Bot

import settings
from helpers import db as db_helper
from helpers import guild as guild_helper
from helpers import bb_api as botbroker

client = Bot('Hello world!')
client.remove_command('help')
token = settings.BOT_USER_TOKEN


def main(argv):
    print("Starting up...")

    @client.event
    async def on_ready():
        print("Preparing commands for sales logging")
        start = time.time()

        channels = {}
        for guild in client.guilds:
            if guild.id in [500010617113935883, 430087124876918798, 697351027728318495, 721742841570787338, 594010666554097664]:
                guild_id = guild.id
                guild_name = guild.name.replace(' ', '_').lower()
                guild_icon = str(guild.icon_url)
                for channel in guild.channels:
                    channel_name = channel.name
                    if channel_name[-1].isdigit():
                        continue
                    if 'other' in channel.name and 'bot' in channel.name:
                        final_bot = 'other'
                        url = f"{settings.DISCORD_URL}/channels/{guild_id}/{channel.id}"
                        channel_type = get_channel_type(channel)
                        if channel_type:
                            db = db_helper.mysql_get_mydb()
                            db_helper.insert_channel(db, {
                                'bot': final_bot,
                                'type': channel_type,
                                'guild_id': guild_id,
                                'guild_name': guild_name,
                                'guild_icon': guild_icon,
                                'channel_name': channel_name,
                                'url': url
                            })
                        continue
                    for bot in settings.ALLOWED_BOTS:
                        aliases = settings.ALLOWED_BOTS[bot]
                        if any(alias in channel.name for alias in aliases):
                            final_bot = bot
                            try:
                                channels[bot] = channels[bot]
                            except KeyError:
                                channels[bot] = {
                                    'wtb': [],
                                    'wts': [],
                                    'wtro': [],
                                    'wtr': [],
                                }
                            url = f"{settings.DISCORD_URL}/channels/{guild_id}/{channel.id}"
                            channel_type = get_channel_type(channel)
                            if channel_type:
                                db = db_helper.mysql_get_mydb()
                                db_helper.insert_channel(db, {
                                    'bot': final_bot,
                                    'type': channel_type,
                                    'guild_id': guild_id,
                                    'guild_name': guild_name,
                                    'guild_icon': guild_icon,
                                    'channel_name': channel_name,
                                    'url': url
                                })
        await client.close()
        print('Finished. Total elapsed time: {}'.format(time.time() - start))

    client.run(token, bot=False)


def get_channel_type(channel):
    if 'wtb' in channel.name:
        return 'wtb'
    elif 'buy' in channel.name:
        if 'rent' in channel.name:
            return 'wtr'
        return 'wtb'
    elif 'wts' in channel.name:
        return 'wts'
    elif 'sell' in channel.name:
        if 'rent' in channel.name:
            return 'wtro'
        return 'wts'
    elif 'wtro' in channel.name:
        return 'wtro'
    elif 'wtr' in channel.name and 'wtro' not in channel.name:
        return 'wtr'
    elif 'rent' in channel.name and 'buy' not in channel.name and 'sell' not in channel.name:
        return 'wtro'
    else:
        return False


if __name__ == "__main__":
    main(sys.argv[1:])
