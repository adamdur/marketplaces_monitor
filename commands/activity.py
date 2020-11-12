import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper


class Activity(BaseCommand):

    def __init__(self):
        description = "Shows activity and average price of selected bot, type and selected days"
                      # "```bot = name of bot // use command '{}available_bots' to see list of available bots\n" \
                      # "renewal_type = [renewal, lt]\n" \
                      # "types = [{}]\n" \
                      # "days = number of days u want to get average price from (max is {})```".format(settings.COMMAND_PREFIX, ", ".join(settings.ACTIVITY_CHANNEL_TYPES), settings.MAX_DAYS_DATA_CAPTURE)
        params = ['bot', 'renewal_type', 'type', 'days']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return

        if params[0] not in settings.ALLOWED_BOTS:
            return await message.channel.send(":x: Bot not available. Use command **{}available_bots** to see list of available bots".format(settings.COMMAND_PREFIX))
        if params[1].lower() not in ['renewal', 'lt']:
            return await message.channel.send(":x: Renewal type not available. Only **[renewal, lt]** renewal types allowed with activity command".format(settings.COMMAND_PREFIX))
        if params[2] not in settings.ACTIVITY_CHANNEL_TYPES:
            return await message.channel.send(":x: Channel type not available. Only **[{}]** types allowed with activity command".format(", ".join(settings.ACTIVITY_CHANNEL_TYPES)))
        if not params[3].isdigit() or int(params[3]) > settings.MAX_DAYS_DATA_CAPTURE:
            return await message.channel.send(":x: Parameter of number of days must be number with max value of **{}**".format(settings.MAX_DAYS_DATA_CAPTURE))

        renewal = 0
        if params[1].lower() == 'lt':
            renewal = 1
        db = db_helper.mysql_get_mydb()
        data = db_helper.get_activity_from(db, params[0], renewal, params[2], params[3])
        if not data:
            return await message.channel.send(":exclamation: Something went wrong while calculating data. Please try again")
        if not data['last_day'] or not data['end_day']:
            return await message.channel.send(":exclamation: No sufficient data found for {}. Try again later...".format(params[0].upper()))

        today = data['last_day']
        today_count = data['last_day_count']
        period = data['end_day']
        period_count = data['end_day_count']
        percentage = (today - period) / period * 100
        percentage_count = (today_count - period_count / int(params[3])) / period_count / int(params[3]) * 100

        if percentage > 0:
            price_change = "up by {0:.2f}% :chart_with_upwards_trend: ".format(percentage)
        else:
            price_change = "down by {0:.2f}% :chart_with_downwards_trend: ".format(percentage)

        if percentage_count > 0:
            price_change_count = "up by {0:.2f}% :chart_with_upwards_trend: ".format(percentage_count)
        else:
            price_change_count = "down by {0:.2f}% :chart_with_downwards_trend: ".format(percentage_count)

        embed = discord.Embed(title="{} {} {}".format(params[0].upper(), params[1].upper(), params[2].upper()), description="", color=settings.DEFAULT_EMBED_COLOR)
        embed.add_field(name="Average price from last {} days:".format(params[3]), value="**{0:.2f}** ({1} posts)".format(period, str(period_count)), inline=True)
        embed.add_field(name="Average price from last 24 hours:", value="**{0:.2f}** ({1} posts)".format(today, str(today_count)), inline=True)
        embed.add_field(name="\u200b", value="**Average price is {}**".format(price_change), inline=False)
        embed.add_field(name="\u200b", value="**Activity is {}**".format(price_change_count), inline=False)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)

        await message.channel.send(embed=embed)
