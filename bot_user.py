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

db = mysql.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_DATABASE,
    user=settings.DB_USER,
    password=settings.DB_PW
)
# cursor = db.cursor()
#
# add_employee = ("INSERT INTO employees "
#                 "(first_name, last_name, hire_date, gender, birth_date) "
#                 "VALUES (%s, %s, %s, %s, %s)")
# add_salary = ("INSERT INTO salaries "
#               "(emp_no, salary, from_date, to_date) "
#               "VALUES (%(emp_no)s, %(salary)s, %(from_date)s, %(to_date)s)")
#
# data_employee = ('Geert', 'Vanderkelen', tomorrow, 'M', date(1977, 6, 14))
#
# # Insert new employee
# cursor.execute(add_employee, data_employee)
# emp_no = cursor.lastrowid
#
# # Insert salary information
# data_salary = {
#     'emp_no': emp_no,
#     'salary': 50000,
#     'from_date': tomorrow,
#     'to_date': date(9999, 1, 1),
# }
# cursor.execute(add_salary, data_salary)
#
# # Make sure data is committed to the database
# db.commit()
#
# cursor.close()

def main():
    @client.event
    async def on_message(message):
        channel_name = message.channel.name
        if any(s in channel_name for s in settings.CHANNELS_IDENTIFIERS):
            if any(negative in channel_name for negative in settings.CHANNELS_NEGATIVE_IDENTIFIERS):
                return

            price_obj = common_helper.get_formatted_price(message)
            price_string = ''
            if price_obj:
                price_string = price_obj['price']
                print("LEVEL: {}".format(price_obj['level']))

            embed = discord.Embed(title="New post in #{}".format(message.channel.name), description="", color=333)
            embed.set_thumbnail(url=message.guild.icon_url)
            embed.add_field(name="Matched price:", value=price_string if price_string else 'N/A', inline=True)
            if message.author.mention:
                embed.add_field(name="Posted by:", value=message.author.mention, inline=True)
            else:
                embed.add_field(name="Posted by:", value=message.author, inline=True)
            embed.add_field(name="Posted in:", value="<#{}>".format(message.channel.id), inline=True)
            embed.add_field(name="Message link:", value=":link: **[VIEW ORIGINAL MESSAGE](https://discord.com/channels/{}/{}/{})**".format(message.guild.id, message.channel.id, message.id), inline=False)
            embed.add_field(name="Message content:", value=">>> {}".format(message.content), inline=False)
            embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=True)
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)

            embed.set_footer(text="[{}]".format(message.guild.name), icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTobiQybVGDOr_cpv9OaKlUOfq_PEEJy5J5fw&usqp=CAU")
            embed.timestamp = message.created_at

            watcher_channel = client.get_channel(settings.DEFAULT_WATCHER_CHANNEL)
            print('sending message')
            await watcher_channel.send(embed=embed)

            if price_obj and price_obj['level'] == 1:
                db_price = common_helper.get_db_price(price_obj['price'])
                db_type = common_helper.get_channel_types(channel_name, message.content)
                if not db_price:
                    return
                if not len(db_type) == 1:
                    return
                bot = common_helper.get_bot_from_channel(channel_name)
                ctype = db_type[0]
                price = db_price
                marketplace = message.guild.name
                created_at = datetime.now()
                content = message.content
                is_lifetime = 1 if any(s in message.content.lower() for s in ['lt', 'lifetime', 'life time', 'life']) else 0
                data = (bot, ctype, price, marketplace, created_at, content, is_lifetime)
                print('TRYING TO SAVE DATA')
                # print('IS LIFETIME: {}'.format(is_lifetime))
                db_helper.insert_post(db, data)
            # insert_query = ("INSERT INTO posts (bot, type, price, marketplace, created_at, content) VALUES (%s, %s, %s, %s, %s, %s)")

    client.run(token, bot=False)


if __name__ == "__main__":
    # db_price = common_helper.get_db_price('1 235')
    main()