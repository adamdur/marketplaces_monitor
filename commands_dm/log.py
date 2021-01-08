import settings
import discord
import datetime
import asyncio

from commands_dm.base_command_dm import BaseCommandDm as BaseCommand

from helpers import db as db_helper


class Log(BaseCommand):

    def __init__(self):
        description = "Log event"
        params = []
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        collector = {
            'event': '',
            'date': '',
            'bot': '',
            'description': '',
            'logged_by': f"{message.author.name}#{message.author.discriminator} <{message.author.id}>",
        }
        event_types = ['bot_update', 'drop_recap', 'release', 'general']

        welcome_embed = discord.Embed(
            title="EVENT LOGGER",
            description="You are going to log an event, here's short info to read.\n"
                        "Feel free to log any kind of events you found but try to focus on events that have potential "
                        "to affect the bot market prices.\n\n"
                        "Currently you can log 4 categories of events. Below you can find short info for each of them",
            color=settings.DEFAULT_EMBED_COLOR
        )
        welcome_embed.add_field(
            name="bot_update",
            value="Add all bot specific updates in this category\n"
                  "e.g.: Cyber 5.0 teaser\n"
                  "Wrath added Wallmart module...",
            inline=False
        )
        welcome_embed.add_field(
            name="drop_recap",
            value="This category is for logging bot drop success\n"
                  "e.g.: Velox flopped / FW20 Supreme week 10 release\n"
                  "Wrath dominated Jordan 1 Mocha release",
            inline=False
        )
        welcome_embed.add_field(
            name="release",
            value="This category is for logging any release and its date\n"
                  "e.g. sneaker release: Jordan 1 Retro High Off-White Chicago\n"
                  "bot release/restock: Cyber public restock",
            inline=False
        )
        welcome_embed.add_field(
            name="general",
            value="This category is for logging any other events.\n"
                  "e.g.: Sole backdoored 100+ copies\n"
                  "MacheteFNF made a call to buy Cyber at $5500",
            inline=False
        )
        await message.author.send(embed=welcome_embed)
        start_embed = discord.Embed(
            title='To start logging, type "start"',
            description="",
            color=settings.DEFAULT_EMBED_COLOR
        )
        await message.author.send(embed=start_embed)

        def check_start(m):
            if not m.guild and m.author == message.author and m.content.lower() == 'start':
                return True
            return False
        try:
            await client.wait_for('message', check=check_start, timeout=60*5)
        except asyncio.TimeoutError:
            return await message.author.send("Session timed out. Start again...")

        event_question_msg = question_event_types(event_types)
        await message.author.send(embed=event_question_msg)

        def check_event_type(m):
            if not m.guild and m.author == message.author:
                response = m.content
                if not response.isnumeric():
                    return False
                if response.isnumeric() and int(response) > len(event_types) + 1:
                    return False
                return True

        response_event = None
        try:
            response_event = await client.wait_for('message', check=check_event_type, timeout=60*5)
        except asyncio.TimeoutError:
            return await message.author.send("Session timed out. Start again...")

        if response_event:
            try:
                collector['event'] = event_types[int(response_event.content) - 1]
            except IndexError:
                return await message.author.send("Unexpected error occurred, start again.")

        date_question_msg = discord.Embed(
            title="",
            description="What's the date of the event?",
            color=settings.DEFAULT_EMBED_COLOR
        )
        date_question_msg.add_field(
            name="Format:",
            value="YYYY-MM-DD\u2003\u2003\u2003\u2003",
            inline=True
        )
        date_question_msg.add_field(
            name="Example:",
            value="2020-12-31",
            inline=True
        )
        await message.author.send(embed=date_question_msg)

        def check_date(m):
            if not m.guild and m.author == message.author:
                response = m.content
                try:
                    datetime.datetime.strptime(response, '%Y-%m-%d')
                    return True
                except ValueError:
                    return False

        response_date = None
        try:
            response_date = await client.wait_for('message', check=check_date, timeout=60*5)
        except asyncio.TimeoutError:
            return await message.author.send("Session timed out. Start again...")

        if response_date:
            try:
                collector['date'] = response_date.content
            except:
                return await message.author.send("Unexpected error occurred, start again.")

        bot_question_msg = discord.Embed(
            title="",
            description="Is the event bot specific?",
            color=settings.DEFAULT_EMBED_COLOR
        )
        bot_question_msg.add_field(
            name="If yes, input the bot name\u2003\u2003\u2003\u2003",
            value="(max 50 characters)",
            inline=True
        )
        bot_question_msg.add_field(
            name='If no, type "none"',
            value="none",
            inline=True
        )
        await message.author.send(embed=bot_question_msg)

        def check_bot(m):
            if not m.guild and m.author == message.author:
                response = m.content
                if response.isnumeric():
                    return False
                if len(response) > 50:
                    return False
                return True

        response_bot = None
        try:
            response_bot = await client.wait_for('message', check=check_bot, timeout=60*5)
        except asyncio.TimeoutError:
            return await message.author.send("Session timed out. Start again...")

        if response_bot:
            try:
                bot = response_bot.content.replace(" ", "_").lower()
                if bot == "none":
                    bot = None
                collector['bot'] = bot
            except:
                return await message.author.send("Unexpected error occurred, start again.")

        description_question_msg = discord.Embed(
            title="",
            description="Write down the short description of the event\nMax 255 characters",
            color=settings.DEFAULT_EMBED_COLOR
        )
        await message.author.send(embed=description_question_msg)

        def check_description(m):
            if not m.guild and m.author == message.author:
                response = m.content
                if response.isnumeric():
                    return False
                if len(response) > 255:
                    return False
                return True

        response_description = None
        try:
            response_description = await client.wait_for('message', check=check_description, timeout=60*5)
        except asyncio.TimeoutError:
            return await message.author.send("Session timed out. Start again...")

        if response_description:
            try:
                collector['description'] = response_description.content
            except:
                return await message.author.send("Unexpected error occurred, start again.")

        validation_msg = discord.Embed(
            title="LOG SUMMARY",
            description="",
            color=settings.DEFAULT_EMBED_COLOR
        )
        for key, value in collector.items():
            validation_msg.add_field(
                name=key,
                value=value if value else "none",
                inline=False
            )

        validation_msg.add_field(
            name="\u200b",
            value="======================================",
            inline=False
        )
        validation_msg.add_field(
            name="To save your log type:\u2003\u2003\u2003\u2003",
            value="save",
            inline=True
        )
        validation_msg.add_field(
            name="To cancel your log and discard changes type:",
            value="cancel",
            inline=True
        )
        await message.author.send(embed=validation_msg)

        def validation(m):
            if not m.guild and m.author == message.author:
                if m.content.lower() in ['save', 'cancel']:
                    return True
            return False
        try:
            response_validation = await client.wait_for('message', check=validation, timeout=60*5)
        except asyncio.TimeoutError:
            return await message.author.send("Session timed out. Start again...")

        if response_validation.content.lower() == 'save':
            try:
                db = db_helper.mysql_get_mydb()
                db_helper.log_event(db, collector)
            except:
                return await message.author.send("Unexpected error occurred while saving. Try again.")
            success_msg = discord.Embed(
                title="",
                description="Log saved successfully. Thank you!",
                color=settings.DEFAULT_EMBED_COLOR
            )
            return await message.author.send(embed=success_msg)
        elif response_validation.content.lower() == 'cancel':
            cancel_msg = discord.Embed(
                title="",
                description="Log canceled. All changes discarded.",
                color=settings.DEFAULT_EMBED_COLOR
            )
            return await message.author.send(embed=cancel_msg)


def question_event_types(event_types):
    embed = discord.Embed(
        title="",
        description="What type of event you want to log?",
        color=settings.DEFAULT_EMBED_COLOR
    )
    types = ""
    for idx, event_type in enumerate(event_types):
        types += f"{idx+1}. {event_type}\n"
    embed.add_field(
        name="Respond with **number** of selected event type",
        value=types,
        inline=True
    )
    return embed
