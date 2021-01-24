import getopt
import sys
from datetime import datetime

import discord
from discord.ext.commands import Bot

import settings
from helpers import common as common_helper
from helpers import db as db_helper

client = Bot('Hello world!')
client.remove_command('help')
token = settings.BOT_USER_TOKEN


def main(argv):
    print("Starting up...")
    print("Everything set up... Watching for messages...")
    print("[DATA TO DATABASE] = ON")

    send_messages = 1
    try:
        opts, args = getopt.getopt(argv, "m:", ["message"])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-m':
            send_messages = arg

    if send_messages == 1:
        print("[DATA TO DISCORD] = ON")
    else:
        print("[DATA TO DISCORD] = OFF")

    @client.event
    async def on_message(message):
        channel_name = message.channel.name
        if any(s in channel_name for s in settings.CHANNELS_IDENTIFIERS):
            # if any(negative in channel_name for negative in settings.CHANNELS_NEGATIVE_IDENTIFIERS):
            #     return

            price_obj = common_helper.get_formatted_price(message)
            embed = build_embed(message, price_obj)
            watcher_channel = client.get_channel(settings.DEFAULT_WATCHER_CHANNEL)

            if send_messages == 1:
                print('-> [SENDING MESSAGE] {} [#{}]'.format(message.guild.name, channel_name))
                await watcher_channel.send(embed=embed)
            insert_log(message, price_obj)

    client.run(token, bot=False)


def build_embed(message, price_object):
    price_string = ''
    price_level = '0'
    if price_object:
        price_string = price_object['price']
        price_level = price_object['level']

    embed = discord.Embed(title="New post in #{}".format(message.channel.name), description="", color=settings.DEFAULT_EMBED_COLOR)
    embed.set_thumbnail(url=message.guild.icon_url)
    embed.add_field(name="Matched price:", value=price_string if price_string else 'N/A', inline=True)
    if message.author.mention:
        embed.add_field(name="Posted by:", value=message.author.mention, inline=True)
    else:
        embed.add_field(name="Posted by:", value=message.author, inline=True)
    embed.add_field(name="Posted in:", value="<#{}>".format(message.channel.id), inline=True)
    embed.add_field(name="Message link:", value=":link: **[MESSAGE]({}/channels/{}/{}/{})**".format(settings.DISCORD_URL, message.guild.id, message.channel.id, message.id), inline=False)
    embed.add_field(name="Message content:", value="{}".format(message.content), inline=False)
    embed.add_field(name="Price level:", value="{}".format(price_level), inline=False)
    embed.add_field(name="Is lifetime:", value="1" if any(s in message.content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else "0", inline=False)
    embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=True)
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)

    embed.set_footer(text="[{}]".format(message.guild.name), icon_url=settings.BOT_ICON)
    embed.timestamp = message.created_at
    return embed


def insert_log(message, price_object):
    db_type = common_helper.get_channel_types(message.channel.name, message.content)
    db_price = None
    data = None
    if not len(db_type) == 1:
        return
    if price_object and price_object['level'] == 1:
        db_price = common_helper.get_db_price(price_object['price'])
    final_type = db_type[0]

    bot_name = common_helper.get_bot_from_channel(message.channel.name)
    if not bot_name:
        return
    if bot_name in ['mek', 'mekpreme'] and 'aio' in message.content.lower():
        bot_name = 'mekaio'

    if (final_type == 'wts' and 'wts' in message.content.lower()) \
            or (final_type == 'wtb' and 'wtb' in message.content.lower()):
        if db_price:
            data = (
                bot_name,
                final_type,
                db_price,
                message.guild.name,
                datetime.now(),
                message.content,
                1 if any(s in message.content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else 0,
                f"{message.author.name}#{message.author.discriminator}",
                f"{message.author.id}",
                f"{settings.DISCORD_URL}/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            )
    elif (final_type == 'wtro' and 'wtro' in message.content.lower()) \
            or (final_type == 'wtr' and 'wtr' in message.content.lower()):
        data = (
            bot_name,
            final_type,
            db_price,
            message.guild.name,
            datetime.now(),
            message.content,
            1 if any(s in message.content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else 0,
            f"{message.author.name}#{message.author.discriminator}",
            f"{message.author.id}",
            f"{settings.DISCORD_URL}/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        )

    if data:
        print('---> SAVING DATA TO DB - {}'.format(final_type))
        db = db_helper.mysql_get_mydb()
        db_helper.insert_post(db, data)


if __name__ == "__main__":
    main(sys.argv[1:])
