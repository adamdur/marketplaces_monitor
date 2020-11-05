import discord
from discord.ext.commands import Bot
import mysql.connector as mysql
import settings
from datetime import date, datetime

from helpers import common as common_helper
from helpers import db as db_helper

client = Bot('Hello world!')
client.remove_command('help')
token = settings.BOT_USER_TOKEN


def main():
    print("Starting up...")
    print("Everything set up... Watching for messages...")

    @client.event
    async def on_message(message):
        channel_name = message.channel.name
        if any(s in channel_name for s in settings.CHANNELS_IDENTIFIERS):
            if any(negative in channel_name for negative in settings.CHANNELS_NEGATIVE_IDENTIFIERS):
                return

            price_obj = common_helper.get_formatted_price(message)
            embed = build_embed(message, price_obj)
            watcher_channel = client.get_channel(settings.DEFAULT_WATCHER_CHANNEL)

            print('-> SENDING MESSAGE')
            await watcher_channel.send(embed=embed)
            insert_log(message, price_obj)

    client.run(token, bot=False)


def build_embed(message, price_object):
    price_string = ''
    if price_object:
        price_string = price_object['price']

    embed = discord.Embed(title="New post in #{}".format(message.channel.name), description="", color=333)
    embed.set_thumbnail(url=message.guild.icon_url)
    embed.add_field(name="Matched price:", value=price_string if price_string else 'N/A', inline=True)
    if message.author.mention:
        embed.add_field(name="Posted by:", value=message.author.mention, inline=True)
    else:
        embed.add_field(name="Posted by:", value=message.author, inline=True)
    embed.add_field(name="Posted in:", value="<#{}>".format(message.channel.id), inline=True)
    embed.add_field(name="Message link:", value=":link: **[VIEW ORIGINAL MESSAGE]({}/channels/{}/{}/{})**".format(settings.DISCORD_URL, message.guild.id, message.channel.id, message.id), inline=False)
    embed.add_field(name="Message content:", value=">>> {}".format(message.content), inline=False)
    embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=True)
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)

    embed.set_footer(text="[{}]".format(message.guild.name), icon_url=settings.BOT_ICON)
    embed.timestamp = message.created_at
    return embed


def insert_log(message, price_object):
    if price_object and price_object['level'] == 1:
        db_price = common_helper.get_db_price(price_object['price'])
        db_type = common_helper.get_channel_types(message.channel.name, message.content)
        if not db_price or not db_type:
            return
        if not len(db_type) == 1:
            return
        if db_type[0] == 'wts' or db_type[0] == 'wtb':
            data = (
                common_helper.get_bot_from_channel(message.channel.name),
                db_type[0],
                db_price,
                message.guild.name,
                datetime.now(),
                message.content,
                1 if any(s in message.content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else 0
            )
            print('---> SAVING DATA TO DB')
            db = db_helper.mysql_get_mydb()
            db_helper.insert_post(db, data)


if __name__ == "__main__":
    main()
