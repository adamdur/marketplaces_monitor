import getopt
import sys
import settings
import discord
import shlex
import re
import redis

from handlers import message_handler
from handlers import message_handler_dm
from helpers import guild as guild_helper
from helpers import common as common_helper
from helpers import setup_data as setup_data_helper
from helpers import channels as channels_helper
from helpers import webhook as webhook_helper
from helpers import db as db_helper
from helpers import redis as redis_helper
from commands.base_command import BaseCommand

this = sys.modules[__name__]
this.running = False
this.setup_data = []
this.TEST_MODE = False


def main(argv):
    print("Starting up...")
    token = settings.BOT_TOKEN
    try:
        opts, args = getopt.getopt(argv, "t:", ["test_mode"])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            print('[USING TEST MODE]')
            this.TEST_MODE = True
            token = settings.BOT_TEST_TOKEN

    db = db_helper.mysql_get_mydb()
    db_helper.save_spammers_to_cache(db)
    SPAMMERS = redis_helper.get_spammers()
    client = discord.Client()

    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        if settings.NOW_PLAYING:
            await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name=settings.NOW_PLAYING))

        # Set the Base guild setup for each guild bot is in
        message_file = f"{settings.BASE_DIR}/messages/info_message.txt"
        message = await setup_data_helper.get_file_content(message_file)
        open(message_file, "w").close()

        verified_guilds = redis_helper.get_verified_guilds()
        if not verified_guilds:
            db = db_helper.mysql_get_mydb()
            verified_guilds = db_helper.get_verified_guilds(db)
        verified_str = "**Verified guilds:**\n"
        unverified_str = "**Unverified guilds:**\n"
        for guild in client.guilds:
            if str(guild.id) not in verified_guilds:
                unverified_str += f"`{guild.name}`\nid: {guild.id}, owner: {str(guild.owner)}\n"
            else:
                guild_data = await guild_helper.base_guild_setup(guild)
                this.setup_data.append(guild_data)
                commands_channel = next(iter(guild_data.values()))['commands_channel']
                if commands_channel and message:
                    await commands_channel.send(message)
                verified_str += f"`{guild.name}`\nid: {guild.id}, owner: {str(guild.owner)}\n"

        verified_str += f"\n{unverified_str}"

        print("Everything set up... Watching marketplaces...")
        await send_webhook("Bot running")
        await send_webhook(verified_str)

        # Load all events
        # print("Loading events...", flush=True)
        # n_ev = 0
        # for ev in BaseEvent.__subclasses__():
        #     event = ev()
        #     sched.add_job(event.run, 'interval', (client,),
        #                   minutes=event.interval_minutes)
        #     n_ev += 1
        # sched.start()
        # print(f"{n_ev} events loaded", flush=True)

    @client.event
    async def on_guild_join(guild):
        db = db_helper.mysql_get_mydb()
        verified_guilds = db_helper.get_verified_guilds(db)
        if str(guild.id) not in verified_guilds:
            await send_webhook(f"**Unverified guild join**\nguild_id: {guild.id}\nguild_name: {guild.name}\nowner: {str(guild.owner)}")
            return
        this.setup_data.append(await guild_helper.base_guild_setup(guild))
        await send_webhook(f"**New guild join**\nguild_id: {guild.id}\nguild_name: {guild.name}\nowner: {str(guild.owner)}")

    @client.event
    async def on_guild_remove(guild):
        await guild_helper.destroy_guild(guild)
        for index, data in enumerate(this.setup_data):
            guild_id = list(data)[0]
            if guild_id == str(guild.id):
                del this.setup_data[index]

    async def bot_sales_handler(message):
        # if message.channel.id in [811971421840474202, 812308435331711026]:
        if message.channel.id == settings.SALES_LOGGER_CHANNEL_ID:
            if message.author.bot:
                try:
                    message_embed = message.embeds[0].to_dict()
                except IndexError:
                    return
                data = []
                if 'bot mart' in message_embed['footer']['text'].lower():
                    server = 'botmart'
                    author_name = message_embed['author']['name'].lower()
                    bot_name = author_name.replace(" sales activity", "")
                    for field in message_embed['fields']:
                        field_name = field['name'].lower()
                        if '24h average' in field_name:
                            renewal_type = field_name[field_name.find("(")+1:field_name.find(")")]
                            renewal_type.replace('$', '')
                            price = field['value']
                            await message.channel.send(f"logged: {server} / {bot_name} / {renewal_type} / {price}")
                            data.append({
                                'server': server,
                                'bot': bot_name.replace(" ", ""),
                                'renewal': renewal_type,
                                'price': price.replace('$', '')
                            })

                elif 'tidal' in message_embed['footer']['text'].lower():
                    server = 'tidal'
                    title = message_embed['title'].lower()
                    bot_name = title.split(' - ')[0]
                    for field in message_embed['fields']:
                        field_name = field['name'].lower()
                        if '24h average' in field_name:
                            renewal_type = field_name[field_name.find("[")+1:field_name.find("]")]
                            renewal_type.replace('$', '')
                            price = field['value']
                            await message.channel.send(f"logged: {server} / {bot_name} / {renewal_type} / {price}")
                            data.append({
                                'server': server,
                                'bot': bot_name.replace(" ", ""),
                                'renewal': renewal_type,
                                'price': price.replace('$', '')
                            })
                elif 'splash market' in message_embed['footer']['text'].lower():
                    server = 'splash'
                    author_name = message_embed['author']['name'].lower()
                    bot_name = author_name.split('-')[0].rsplit(' ', 1)[0]
                    for field in message_embed['fields']:
                        renewal_type = field['name'].lower()
                        field_value = field['value'].lower()
                        start = field_value.find("daily average**: ") + len("daily average**: ")
                        end = field_value.find("**weekly average")
                        price = field_value[start:end].strip()
                        await message.channel.send(f"logged: {server} / {bot_name} / {renewal_type} / {price}")
                        data.append({
                            'server': server,
                            'bot': bot_name.replace(" ", ""),
                            'renewal': renewal_type,
                            'price': price.replace('$', '')
                        })
                if data:
                    idx = 0
                    for row in data:
                        new_bot_name = handle_bot_name(data[0]['bot'])
                        data[idx]['bot'] = new_bot_name
                        idx += 1
                    db = db_helper.mysql_get_mydb()
                    logged = db_helper.log_sale(db, data)

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        if message.author.bot:
            return
        if not message.guild:
            try:
                return await message_handler_dm.handle_command(message, client)
            except:
                print("Error while handling DM message", flush=True)
                raise
        if text.startswith(settings.COMMAND_PREFIX) and text != settings.COMMAND_PREFIX:
            cmd_split = shlex.split(text[len(settings.COMMAND_PREFIX):])

            is_verified = await is_verified_guild(message, cmd_split[0].lower())
            if not is_verified:
                return

            if cmd_split[0].lower() in settings.ADMIN_COMMANDS:
                if not [role for role in message.author.roles if role.name.lower() in settings.ALLOWED_ROLES]:
                    return
            try:
                await message_handler.handle_command(cmd_split[0].lower(), cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise

    async def common_watcher_handle_message(message):
        # ticket monitor is not used, temporarily turning off
        # if message.channel.id == settings.DEFAULT_TICKET_WATCHER_CHANNEL:
        #     await handle_ticket_monitor(client, message)

        if message.channel.id == settings.DEFAULT_WATCHER_CHANNEL:
            if not message.embeds:
                return

            embed = message.embeds[0]
            if not embed:
                return

            embed_dict = embed.to_dict()
            message_channel = embed_dict['title'].split("#")[1]

            message_content = ''
            price_str = ''
            price_level = ''
            is_lifetime = ''
            for index, field in enumerate(embed_dict['fields']):
                if field['name'] == 'Matched price:':
                    price_str = field['value']
                elif field['name'] == 'Posted by:':
                    message_user = field['value']
                elif field['name'] == 'Posted in:':
                    message_posted_in = field['value']
                elif field['name'] == 'Message link:':
                    message_link = field['value']
                elif field['name'] == 'Message content:':
                    message_content = field['value']
                elif field['name'] == 'Price level:':
                    price_level = field['value']
                elif field['name'] == 'Is lifetime:':
                    is_lifetime = field['value']

            dic = {'<': '', '>': '', '@': '', '!': ''}
            user_id = message_user
            if user_id:
                for i, j in dic.items():
                    user_id = user_id.replace(i, j)

            final_types = common_helper.get_channel_types(message_channel, message_content)
            final_bot = common_helper.get_bot_from_channel(message_channel)
            if not final_bot:
                if not any(negative in message_channel for negative in settings.CHANNELS_NEGATIVE_IDENTIFIERS):
                    await send_webhook(f"@here \n Unknown bot channel found: **#{message_channel}**")

            if final_bot in ['mek', 'mekpreme']:
                if any(x in message.content.lower() for x in ['aio']):
                    final_bot = 'mekaio'

            final_channels = []
            message_data = None
            if final_bot and final_types:
                for type in final_types:
                    final_channels.append("{}-{}".format(final_bot, type))
                    if price_level and price_str:
                        if type in ['wts', 'wtb'] and int(price_level) == 1:
                            message_data = common_helper.build_status_message(final_bot, price_str, type, is_lifetime)
            clean_embed = discord.Embed(
                title="",
                description=f"{message_content}\n\n"
                            f"{'' if price_str == 'N/A' else price_str + ' | '}{message_link} | {message_user}\n"
                            f"{message_data['message'] if message_data else ''}\n\n",
                color=settings.DEFAULT_EMBED_COLOR
            )
            clean_embed.set_author(name=f"{embed.author.name} #{message_channel}", icon_url=embed.author.icon_url)
            clean_embed.timestamp = message.created_at

            verified_guilds = redis_helper.get_verified_guilds()
            if not verified_guilds:
                db = db_helper.mysql_get_mydb()
                verified_guilds = db_helper.get_verified_guilds(db)

            for data in this.setup_data:
                guild_id = list(data)[0]
                if str(guild_id) not in verified_guilds:
                    print(f"Non verified guild found: {guild_id}")
                    return

                if guild_id == '726811962742407211':
                    if user_id in SPAMMERS:
                        print(f"SPAMMER POST FOUND {user_id}")
                        return

                setup = await setup_data_helper.get_data_by_id(guild_id)
                channels = setup['channels']
                channel_names = list(channels.keys())
                guild_data = guild_helper.get_guild_by_id(client.guilds, int(guild_id))
                clean_embed.set_footer(text=f"[{guild_data.name}]", icon_url=guild_data.icon_url)

                kw_channels = await setup_data_helper.get_keyword_channels(channels)
                for idx, kw_channel in kw_channels.items():
                    try:
                        kws = kw_channel['keywords']
                        _post = True
                        for kw in kws:
                            kw_options = kw.split('|')
                            if not any(kw_option.lower() in message_content.lower() for kw_option in kw_options):
                                _post = False
                                break
                        if not _post:
                            continue
                        if _post:
                            kw_channel_to_post = channels_helper.get_channel_by_id(data[guild_id]['guild'].channels, kw_channel['id'])
                            print('---> GOING TO POST IN KW CHANNEL #{} - {}'.format(idx, guild_data.name))
                            try:
                                await kw_channel_to_post.send(embed=clean_embed)
                            except AttributeError:
                                await webhook_helper.send_invalid_channel_webhook(guild_id, guild_data.name, idx)
                    except KeyError:
                        continue

                for final_channel in final_channels:
                    if final_channel in channel_names:
                        channel_id = channels[final_channel]['id']

                        channel_to_post = channels_helper.get_channel_by_id(data[guild_id]['guild'].channels, channel_id)

                        notify_guild = guild_helper.get_guild_by_id(client.guilds, int(guild_id))
                        pings = await setup_data_helper.get_pings_for_channel(notify_guild, final_channel)
                        notify_handles = ''
                        if pings:
                            bot_name, channel_type = final_channel.split('-')
                            if channel_type in ['wts', 'wtb']:
                                notify_handles = ''
                                for handle_price, handles in pings.items():
                                    if handles and price_str != 'N/A' and int(price_level) == 1:
                                        int_price = common_helper.get_db_price(price_str)
                                        notify_with_handle = False
                                        if channel_type == 'wts':
                                            if int(handle_price) > int(int_price):
                                                notify_with_handle = True
                                        elif channel_type == 'wtb':
                                            if int(handle_price) < int(int_price):
                                                notify_with_handle = True
                                        if notify_with_handle:
                                            for handle in handles:
                                                notify_handles += ' ' + handle
                        print('---> GOING TO POST IN #{} - {}'.format(final_channel, guild_data.name))
                        try:
                            await channel_to_post.send(embed=clean_embed, content=notify_handles)
                        except AttributeError:
                            await webhook_helper.send_invalid_channel_webhook(guild_id, guild_data.name, final_channel)

    @client.event
    async def on_message(message):
        await common_handle_message(message)
        await common_watcher_handle_message(message)
        await bot_sales_handler(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)
        await bot_sales_handler(after)

    client.run(token)

###############################################################################


def handle_bot_name(bot):
    if bot in ['burstaio']:
        bot = 'burst'
    elif bot in ['eveaio']:
        bot = 'eve'
    elif bot in ['f3ather', 'f3atherio']:
        bot = 'f3'
    elif bot in ['fleekframework']:
        bot = 'fleek'
    elif bot in ['ganeshbot']:
        bot = 'ganesh'
    elif bot in ['kageaio']:
        bot = 'kage'
    elif bot in ['mekpreme']:
        bot = 'mek'
    elif bot in ['mercuryaio']:
        bot = 'mercury'
    elif bot in ['polarisaio']:
        bot = 'polaris'
    elif bot in ['prismaio']:
        bot = 'prism'
    elif bot in ['rushaio']:
        bot = 'rush'
    elif bot in ['splashforce']:
        bot = 'sf'
    elif bot in ['soleaio']:
        bot = 'sole'
    elif bot in ['torpedoaio']:
        bot = 'torpedo'
    elif bot in ['veloxpreme']:
        bot = 'velox'
    elif bot in ['balkobot']:
        bot = 'balko'
    elif bot in ['flareaio']:
        bot = 'flare'
    elif bot in ['kiloaio']:
        bot = 'kilo'
    elif bot in ['koisolutions']:
        bot = 'koi'
    elif bot in ['lexaio']:
        bot = 'lex'
    return bot


async def send_webhook(message):
    await webhook_helper.send_webhook(message, this.TEST_MODE)


async def is_verified_guild(message, command):
    verified_guilds = redis_helper.get_verified_guilds()
    if not verified_guilds:
        db = db_helper.mysql_get_mydb()
        verified_guilds = db_helper.get_verified_guilds(db)
    if str(message.guild.id) not in verified_guilds:
        COMMAND_HANDLERS = {c.__name__.lower(): c() for c in BaseCommand.__subclasses__()}
        if command in COMMAND_HANDLERS:
            embed = discord.Embed(
                title="",
                description=f"**This server is not authorized to use this tool**\n"
                            f"Join [MARKETEX SERVER](https://discord.gg/9XTKvHtJsP) to learn more about activation.",
                color=settings.DEFAULT_EMBED_COLOR
            )
            await message.channel.send(embed=embed)
        print(f"Non verified guild found: {message.guild.id} / {message.guild.name}")
        return False
    return True


async def handle_ticket_monitor(client, message):
    if not message.embeds:
        return
    embed = message.embeds[0]
    if not embed:
        return
    embed_dict = embed.to_dict()

    marketplace = ''
    for index, field in enumerate(embed_dict['fields']):
        if field['name'] == 'Server:':
            marketplace = field['value']
            embed.remove_field(index)

    embed.timestamp = message.created_at

    db = db_helper.mysql_get_mydb()
    monitor_channels = db_helper.get_ticket_monitors(db, marketplace)
    for monitor in monitor_channels:
        try:
            guild = guild_helper.get_guild_by_id(client.guilds, int(monitor['guild_id']))
            channel = guild.get_channel(int(monitor['channel_id']))
            embed.set_footer(text=f"[{guild.name}]", icon_url=guild.icon_url)
            await channel.send(embed=embed)
        except:
            print(f"UNABLE TO POST TICKET INTO CHANNEL {monitor['channel_id']} IN GUILD {monitor['guild_id']}")


if __name__ == "__main__":
    main(sys.argv[1:])
