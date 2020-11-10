import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper


class Activity_stats(BaseCommand):

    def __init__(self):
        description = "Shows activity and average price of selected bot, type and selected days" \
                      "```renewal_type = [renewal, lt]\n" \
                      "types = [{}]\n" \
                      "days = number of days u want to get average price from (max is {})```".format(", ".join(settings.ACTIVITY_CHANNEL_TYPES), settings.MAX_DAYS_DATA_CAPTURE)
        params = ['renewal_type', 'type', 'days']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return
        renewal_type = params[0]
        type = params[1]
        days = params[2]

        if renewal_type.lower() not in ['renewal', 'lt']:
            return await message.channel.send(":x: Renewal type not available. Only **[renewal, lt]** renewal types allowed with activity command".format(settings.COMMAND_PREFIX))
        if type not in settings.ACTIVITY_CHANNEL_TYPES:
            return await message.channel.send(":x: Channel type not available. Only **[{}]** types allowed with activity command".format(", ".join(settings.ACTIVITY_CHANNEL_TYPES)))
        if not days.isdigit() or int(days) > settings.MAX_DAYS_DATA_CAPTURE:
            return await message.channel.send(":x: Parameter of number of days must be number with max value of **{}**".format(settings.MAX_DAYS_DATA_CAPTURE))

        renewal = 0
        if renewal_type.lower() == 'lt':
            renewal = 1
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_activity_stats(db, renewal, type, days)

        if not data:
            return await message.channel.send(":exclamation: Something went wrong while calculating data. Please try again")

        price_list = data['price_list']
        count_list = data['count_list']
        price_list_str = ''
        count_list_str = ''
        index = 1
        idx = 1
        for price in price_list[:15]:
            price_list_str += '**{0}. {1}**\n'.format(index, price['bot'].capitalize())
            price_list_str += '> :green_circle: **\u2002+' if price['average_price_percentage'] > 0 else '> :red_circle: **\u2002'
            price_list_str += '{0:.2f}%**\u2002(${1:.0f})\n'.format(price['average_price_percentage'], price['average_price'])
            index += 1
        for count in count_list[:15]:
            count_list_str += '**{0}. {1}**\n'.format(idx, count['bot'].capitalize())
            count_list_str += '> :green_circle: **\u2002+' if count['count_percentage'] > 0 else '> :red_circle: **\u2002'
            count_list_str += '{0:.2f}%**\u2002({1:.0f} posts)\n'.format(count['count_percentage'], count['count'])
            idx += 1

        description = "Data structure legend:\n" \
                      "> **[status] [movement] ([current])**\n" \
                      "> **status** = price is up :green_circle: / down :red_circle:\n" \
                      "> **movement** = percentage movement in last 24 hours compared to {} days before\n" \
                      "> **current** = average price / number of posts in last 24 hours\n\n".format(days, days)
        embed = discord.Embed(title="{} BOTS {} ACTIVITY STATS".format(renewal_type.upper(), type.upper()), description=description, color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="Average price increase/decrease:\u2002\u2002".format(days), value=price_list_str, inline=True)
        embed.add_field(name="Average activity increase/decrease:", value=count_list_str, inline=True)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)
        await message.channel.send(embed=embed)
