import getopt
import sys
import shlex
from datetime import datetime

import discord
from discord.ext.commands import Bot
import discum

import settings
from helpers import common as common_helper
from helpers import db as db_helper

client = Bot('Hey')
client.remove_command('help')
token = settings.BOT_USER_TOKEN
bot = discum.Client(token=settings.BOT_USER_TOKEN, log=False)


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
        if message.guild.id not in settings.MARKETPLACES_GUILD_IDS:
            return
        channel_name = message.channel.name
        if any(s in channel_name for s in settings.CHANNELS_IDENTIFIERS):
            resp = bot.getMessage(str(message.channel.id), str(message.id))
            content = resp.json()[0]['content']
            price_obj = common_helper.get_formatted_price(message, content)
            embed = build_embed(message, price_obj, content)
            watcher_channel = client.get_channel(settings.DEFAULT_WATCHER_CHANNEL)

            if send_messages == 1:
                print('-> [SENDING MESSAGE] {} [#{}]'.format(message.guild.name, channel_name))
                await watcher_channel.send(embed=embed)
            insert_log(message, price_obj, content)
        elif 'ticket' in channel_name.lower():
            # ticket_channel = client.get_channel(settings.DEFAULT_TICKET_WATCHER_CHANNEL)
            resp = bot.getMessage(str(message.channel.id), str(message.id))
            content = resp.json()[0]['content'].lower()
            ticket_command = content.split()
            if ticket_command and 'new' in ticket_command[0]:
                # embed = build_embed_ticket(message, ticket_command)
                # await ticket_channel.send(embed=embed)
                insert_log_ticket(message, ticket_command, content)

    client.run(token, bot=False)
    bot.gateway.run(auto_reconnect=True)


def build_embed_ticket(message, command):
    embed = discord.Embed(
        title="",
        description=f"{message.content}\n"
                    f":link: [MESSAGE]({settings.DISCORD_URL}/channels/{message.guild.id}/{message.channel.id}/{message.id}) | {message.author.mention}",
        color=settings.DEFAULT_EMBED_COLOR
    )
    server = ''
    if message.guild.id == 500010617113935883:
        server = 'tidal'
    elif message.guild.id == 430087124876918798:
        server = 'botmart'
    elif message.guild.id == 697351027728318495:
        server = 'splash'
    elif message.guild.id == 594010666554097664:
        server = 'didi'
    elif message.guild.id == 721742841570787338:
        server = 'tiger'
    embed.add_field(name="Server:", value=f"{server}", inline=True)
    embed.set_author(name=f"New ticket request in {message.guild.name}", icon_url=message.guild.icon_url)
    embed.timestamp = message.created_at
    return embed


def insert_log_ticket(message, command, content):
    data = (
        " ".join(command[1:]),
        message.guild.id,
        message.guild.name,
        content,
        f"{message.author.name}#{message.author.discriminator}",
        f"{message.author.id}",
        f"{settings.DISCORD_URL}/channels/{message.guild.id}/{message.channel.id}/{message.id}",
        datetime.now()
    )
    if data:
        print(f"---> SAVING DATA TO DB - TICKET")
        db = db_helper.mysql_get_mydb()
        db_helper.insert_post_ticket(db, data)


def build_embedx(message, price_object, channel_name, guild):
    price_string = ''
    price_level = '0'
    if price_object:
        price_string = price_object['price']
        price_level = price_object['level']

    embed = discord.Embed(title="New post in #{}".format(channel_name), description="", color=settings.DEFAULT_EMBED_COLOR)
    embed.set_thumbnail(url=message.guild.icon_url)
    embed.add_field(name="Matched price:", value=price_string if price_string else 'N/A', inline=True)
    embed.add_field(name="Posted by:", value=f"<@!{message['author']['id']}>", inline=True)
    # if message.author.mention:
    #     embed.add_field(name="Posted by:", value=message.author.mention, inline=True)
    # else:
    #     embed.add_field(name="Posted by:", value=message.author, inline=True)
    embed.add_field(name="Posted in:", value="<#{}>".format(message['channel_id']), inline=True)
    embed.add_field(name="Message link:", value=":link: [MESSAGE]({}/channels/{}/{}/{})".format(settings.DISCORD_URL, message['guild_id'], message['channel_id'], message['id']), inline=False)
    embed.add_field(name="Message content:", value="{}".format(message['content']), inline=False)
    embed.add_field(name="Price level:", value="{}".format(price_level), inline=False)
    embed.add_field(name="Is lifetime:", value="1" if any(s in message['content'].lower() for s in ['lt', 'lifetime', 'life time', 'life']) else "0", inline=False)
    embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=True)
    embed.set_author(name=guild.name, icon_url=guild.icon_url)

    embed.set_footer(text="[{}]".format(guild.name), icon_url=settings.BOT_ICON)
    embed.timestamp = message['timestamp']
    return embed


def build_embed(message, price_object, content):
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
    embed.add_field(name="Message link:", value=":link: [MESSAGE]({}/channels/{}/{}/{})".format(settings.DISCORD_URL, message.guild.id, message.channel.id, message.id), inline=False)
    embed.add_field(name="Message content:", value=f"{content if content else 'N/A'}", inline=False)
    embed.add_field(name="Price level:", value="{}".format(price_level), inline=False)
    embed.add_field(name="Is lifetime:", value="1" if any(s in message.lower() for s in ['lt', 'life']) else "0", inline=False)
    embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=True)
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)

    embed.set_footer(text="[{}]".format(message.guild.name), icon_url=settings.BOT_ICON)
    embed.timestamp = message.created_at
    return embed


def insert_log(message, price_object, content):
    db_type = common_helper.get_channel_types(message.channel.name, content)
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
    if bot_name in ['mek', 'mekpreme'] and 'aio' in content.lower():
        bot_name = 'mekaio'

    if (final_type == 'wts' and 'wts' in content.lower()) \
            or (final_type == 'wtb' and 'wtb' in content.lower()):
        if db_price:
            data = (
                bot_name,
                final_type,
                db_price,
                message.guild.name,
                datetime.now(),
                content,
                1 if any(s in content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else 0,
                f"{message.author.name}#{message.author.discriminator}",
                f"{message.author.id}",
                f"{settings.DISCORD_URL}/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            )
    elif (final_type == 'wtro' and 'wtro' in content.lower()) \
            or (final_type == 'wtr' and 'wtr' in content.lower()):
        data = (
            bot_name,
            final_type,
            db_price,
            message.guild.name,
            datetime.now(),
            content,
            1 if any(s in content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else 0,
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
