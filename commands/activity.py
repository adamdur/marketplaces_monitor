import settings
import discord

from commands.base_command import BaseCommand

from helpers import channels as channels_helper
from helpers import db as db_helper
from helpers import common as common_helper
from helpers import errors as errors_helper


class Activity(BaseCommand):

    def __init__(self):
        description = "Shows activity and average price of selected bot, type and selected days"
        params = ['bot']
        params_optional = ['channel_type', 'days']
        guide = f'{settings.COMMANDS_GUIDE_URL}#heading=h.hbt0417dv97p'
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        is_commands_channel = await channels_helper.is_commands_channel(message)
        if not is_commands_channel:
            return

        bot = common_helper.get_param_by_index(params, 0)
        type = common_helper.get_optional_param_by_index(params_optional, 0, "wtb")
        days = common_helper.get_optional_param_by_index(params_optional, 1, "1")

        if not await errors_helper.check_bot_param(bot, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_days_param(days, message.channel, guide=self.guide):
            return
        if not await errors_helper.check_type_param(type, message.channel, guide=self.guide):
            return

        db = db_helper.mysql_get_mydb()
        data = db_helper.get_activity_from(db, bot, type, days)

        if not await errors_helper.check_db_response(data, message.channel):
            return
        if not data['renewal'] and not data['lifetime']:
            return await message.channel.send(":exclamation: No sufficient data found for {}. Try again later...".format(bot.upper()))

        embed = discord.Embed(title="{} {} ACTIVITY STATS".format(bot.upper(), type.upper()), description="", color=settings.DEFAULT_EMBED_COLOR)
        append_embed_data(embed, data, days)
        embed.add_field(name="\u200b", value="[{}]({})".format(settings.BOT_NAME, settings.BOT_URL), inline=False)

        await message.channel.send(embed=embed)


def append_embed_data(embed, data, days):
    for renewal, values in data.items():
        try:
            today = values['last_day']
            today_count = values['last_day_count']
            period = values['end_day']
            period_count = values['end_day_count']
        except KeyError:
            continue
        percentage = (today - period) / period * 100
        percentage_count = (today_count - period_count / int(days)) / period_count / int(days) * 100

        if percentage > 0:
            price_change = "up by {0:.2f}% :chart_with_upwards_trend: ".format(percentage)
        else:
            price_change = "down by {0:.2f}% :chart_with_downwards_trend: ".format(percentage)

        if percentage_count > 0:
            price_change_count = "up by {0:.2f}% :chart_with_upwards_trend: ".format(percentage_count)
        else:
            price_change_count = "down by {0:.2f}% :chart_with_downwards_trend: ".format(percentage_count)

        days_str = common_helper.get_time_string_from_days(days)

        embed.add_field(name="\u200b", value="> *{}*".format(renewal.upper()), inline=False)
        embed.add_field(name="*Average price from {} before last 24 hours:*\u2002\u2002".format(days_str), value="**{0:.2f}** ({1} posts)".format(period, str(period_count)), inline=True)
        embed.add_field(name="*Average price from last 24 hours:*", value="**{0:.2f}** ({1} posts)".format(today, str(today_count)), inline=True)
        embed.add_field(name="**Average price is {}**".format(price_change), value="**Activity is {}**".format(price_change_count), inline=False)

    return embed
