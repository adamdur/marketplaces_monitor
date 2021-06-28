import sys
import time

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
        db = db_helper.mysql_get_mydb()
        bots = db_helper.get_sotm_commands(db)
        print("Executing commands...")
        for bot in bots:
            bot_commands = bot['commands'].split(',')
            for command in bot_commands:
                guild = guild_helper.get_guild_by_id(client.guilds, settings.SALES_LOGGER_SERVER_ID)
                channel = guild.get_channel(settings.SALES_LOGGER_CHANNEL_ID)
                await channel.send(command)
                time.sleep(10)
            if bot['botbroker']:
                bb_bid = await botbroker.get_highest_bid(bot['botbroker'], 'lifetime' if 'lifetime' in bot['renewal'] else 'renewal')
                try:
                    if bb_bid['price']:
                        new_bot_name = handle_bot_name(bot['bot'])
                        bb_data = [{
                            'server': 'botbroker',
                            'bot': new_bot_name,
                            'renewal': 'lifetime' if 'lifetime' in bot['renewal'] else 'renewal',
                            'price': str(bb_bid['price'])
                        }]
                        db = db_helper.mysql_get_mydb()
                        logged = db_helper.log_sale(db, bb_data)
                except:
                    print(f"Unable to log botbroker sale for {bot['bot']}")
                    continue
        await client.close()
        print('Finished. Total elapsed time: {}'.format(time.time() - start))

    client.run(token, bot=False)


def handle_bot_name(bot):
    if bot in ['burstaio']:
        bot = 'burst'
    elif bot in ['eveaio']:
        bot = 'eve'
    elif bot in ['f3ather', 'f3atherio']:
        bot = 'f3'
    elif bot in ['fleekframework']:
        bot = 'fleek'
    elif bot in ['ganeshbot']:
        bot = 'ganesh'
    elif bot in ['kageaio']:
        bot = 'kage'
    elif bot in ['mekpreme']:
        bot = 'mek'
    elif bot in ['mercuryaio']:
        bot = 'mercury'
    elif bot in ['polarisaio']:
        bot = 'polaris'
    elif bot in ['prismaio']:
        bot = 'prism'
    elif bot in ['rushaio']:
        bot = 'rush'
    elif bot in ['splashforce']:
        bot = 'sf'
    elif bot in ['soleaio']:
        bot = 'sole'
    elif bot in ['torpedoaio']:
        bot = 'torpedo'
    elif bot in ['veloxpreme']:
        bot = 'velox'
    elif bot in ['balkobot']:
        bot = 'balko'
    elif bot in ['flareaio']:
        bot = 'flare'
    elif bot in ['kiloaio']:
        bot = 'kilo'
    elif bot in ['koisolutions']:
        bot = 'koi'
    elif bot in ['lexaio']:
        bot = 'lex'
    return bot


if __name__ == "__main__":
    main(sys.argv[1:])
