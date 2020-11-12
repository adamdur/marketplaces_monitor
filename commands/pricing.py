import settings
import discord
import math

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper


class Pricing(BaseCommand):

    def __init__(self):
        description = "Shows bots sorted by average price at a given time"
                      # "```types = [{}]\n" \
                      # "days = number of days you want to get average price from (max is {})```".format(", ".join(settings.ACTIVITY_CHANNEL_TYPES), settings.MAX_DAYS_DATA_CAPTURE)
        params = ['type', 'days']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return
        type = params[0]
        days = params[1]

        if type not in settings.ACTIVITY_CHANNEL_TYPES:
            return await message.channel.send(":x: Channel type not available. Only **[{}]** types allowed with activity command".format(", ".join(settings.ACTIVITY_CHANNEL_TYPES)))
        if not days.isdigit() or int(days) > settings.MAX_DAYS_DATA_CAPTURE:
            return await message.channel.send(":x: Parameter of number of days must be number with max value of **{}**".format(settings.MAX_DAYS_DATA_CAPTURE))

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_price_stats(db, type, days)

        if not data:
            return await message.channel.send(":exclamation: Something went wrong while calculating data. Please try again")

        index = 1
        stats_str = ''
        stats_str_scnd = ''
        for bot in data:
            daily_count = int(bot['price'])
            if daily_count >= 5500:
                status = ':fire:'
            elif 5500 > daily_count >= 3500:
                status = ':blue_circle:'
            elif 3500 > daily_count >= 2000:
                status = ':green_circle:'
            elif 2000 > daily_count >= 1000:
                status = ':yellow_circle:'
            elif 1000 > daily_count >= 450:
                status = ':orange_circle:'
            else:
                status = ':red_circle:'
            if index <= math.ceil(len(data) / 2):
                stats_str += status + ' {0}. {1}\u2002|\u2002**${2:.0f}**\n'.format(index, bot['bot'].capitalize(), bot['price'])
            else:
                stats_str_scnd += status + ' {0}. {1}\u2002|\u2002**${2:.0f}**\n'.format(index, bot['bot'].capitalize(), bot['price'])
            index += 1

        if days == '1':
            days_str = '24 hours'
        else:
            days_str = days + ' days'

        description = "**Bots sorted by average price of {} posts in last {}:**"
                      # ":fire: $5500+ \u2003\u2003\u2003\u2003\u2003\u2003 :yellow_circle: $1000 - $2000\n" \
                      # ":blue_circle: $3500 - $5500 \u2003\u2003\u2003 :orange_circle: $450 - $1000\n" \
                      # ":green_circle: $2000 - $3500 \u2003\u2003\u2003 :red_circle: $450 >"
        embed = discord.Embed(title="{} POSTS STATS".format(type.upper()), description=description.format(type.upper(), days_str), color=settings.DEFAULT_EMBED_COLOR)
        # embed.add_field(name="Bots sorted by number of {} posts in last {}:".format(type.upper(), days_str), value="", inline=False)
        embed.add_field(name="\u200b", value=stats_str, inline=True)
        embed.add_field(name="\u200b", value=stats_str_scnd, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
