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
                        bb_data = [{
                            'server': 'botbroker',
                            'bot': bot['bot'],
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


if __name__ == "__main__":
    main(sys.argv[1:])
