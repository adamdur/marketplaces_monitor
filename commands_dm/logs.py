import settings
import discord
import datetime

from commands_dm.base_command_dm import BaseCommandDm as BaseCommand

from helpers import db as db_helper


class Logs(BaseCommand):

    def __init__(self):
        description = "Logs list"
        params = ['date']
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        try:
            date = params[0]
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return await message.author.send("Bad date format. Use format **YYYY-MM-DD**")
        except IndexError:
            return await message.author.send("Add date as a first parameter in format **YYYY-MM-DD**")
        try:
            db = db_helper.mysql_get_mydb()
            data = db_helper.get_event_logs(db, date)
        except:
            return await message.author.send("Unexpected error occurred. Try again.")

        embed = discord.Embed(
            title="EVENT LOGS",
            description=f"List of event logs for date **{date}**",
            color=settings.DEFAULT_EMBED_COLOR
        )
        if not data:
            embed.add_field(
                name=f"No logs for date {date}",
                value="\u200b",
                inline=False
            )
        if data:
            for item in data:
                field_value = ""
                for key, value in item.items():
                    if not key == "date":
                        if key == "logged_by":
                            field_value += f"**{key}:** {value.split(' ')[0]}\n"
                        else:
                            field_value += f"**{key}:** {value}\n"
                embed.add_field(
                    name=item['date'],
                    value=field_value,
                    inline=False
                )
        return await message.author.send(embed=embed)
