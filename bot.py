import getopt
import sys
import settings
import discord
import shlex

from handlers import message_handler
from handlers import message_handler_dm
from helpers import guild as guild_helper
from helpers import common as common_helper
from helpers import setup_data as setup_data_helper
from helpers import channels as channels_helper
from helpers import webhook as webhook_helper

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
        for guild in client.guilds:
            if int(guild.id) in settings.VERIFIED_GUILDS:
                guild_data = await guild_helper.base_guild_setup(guild)
                this.setup_data.append(guild_data)
                commands_channel = next(iter(guild_data.values()))['commands_channel']
                if commands_channel and message:
                    await commands_channel.send(message)
            else:
                await guild.leave()

        print("Everything set up... Watching marketplaces...")
        await send_webhook("Bot running")

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
        if int(guild.id) in settings.VERIFIED_GUILDS:
            this.setup_data.append(await guild_helper.base_guild_setup(guild))
        else:
            await guild.leave()

    @client.event
    async def on_guild_remove(guild):
        await guild_helper.destroy_guild(guild)
        for index, data in enumerate(this.setup_data):
            guild_id = list(data)[0]
            if guild_id == str(guild.id):
                del this.setup_data[index]

    @client.event
    async def on_disconnect():
        print("Bot disconnected")
        # await send_webhook("@here Bot disconnected")

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
            if cmd_split[0].lower() in settings.ADMIN_COMMANDS:
                if not [role for role in message.author.roles if role.name.lower() in settings.ALLOWED_ROLES]:
                    return
            try:
                await message_handler.handle_command(cmd_split[0].lower(), cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise

    async def common_watcher_handle_message(message):
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
            remove_indexes = []
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
                    remove_indexes.append(index)
                elif field['name'] == 'Is lifetime:':
                    is_lifetime = field['value']
                    remove_indexes.append(index)

            # for remove_index in sorted(remove_indexes, key=int, reverse=True):
            #     embed.remove_field(remove_index)

            final_types = common_helper.get_channel_types(message_channel, message_content)
            if not final_types:
                print('No type found: {}'.format(message_channel))

            final_bot = common_helper.get_bot_from_channel(message_channel)
            if not final_bot:
                print('Bot not found: {}'.format(message_channel))
                if not any(negative in message_channel for negative in settings.CHANNELS_NEGATIVE_IDENTIFIERS):
                    await send_webhook(f"@here \n Unknown bot channel found: **#{message_channel}**")

            if final_bot in ['mek', 'mekpreme']:
                if any(x in message.content.lower() for x in ['aio']):
                    final_bot = 'mekaio'

            final_channels = []
            notify = False
            message_data = None
            if final_bot and final_types:
                for type in final_types:
                    final_channels.append("{}-{}".format(final_bot, type))
                    if price_level and price_str:
                        if type in ['wts', 'wtb'] and int(price_level) == 1:
                            message_data = common_helper.build_status_message(final_bot, price_str, type, is_lifetime)
                            if message_data:
                                if message_data['notify'] is True:
                                    notify = True
            clean_embed = discord.Embed(
                title="",
                description=f"{message_content}\n\n"
                            f"{'' if price_str == 'N/A' else price_str + ' | '}{message_link} | {message_user}\n"
                            f"{message_data['message'] if message_data else ''}\n\n",
                color=settings.DEFAULT_EMBED_COLOR
            )
            clean_embed.set_author(name=f"{embed.author.name} #{message_channel}", icon_url=embed.author.icon_url)
            clean_embed.timestamp = message.created_at

            for data in this.setup_data:
                guild_id = list(data)[0]
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
                            print('---> GOING TO POST IN KW CHANNEL #{}'.format(idx))
                            await kw_channel_to_post.send(embed=clean_embed)
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
                        print('---> GOING TO POST IN #{} - {}'.format(final_channel, guild_id))
                        # clean_embed.set_footer(text=f"[{notify_guild.name}]", icon_url=notify_guild.icon_url)
                        await channel_to_post.send(embed=clean_embed, content=notify_handles)

    @client.event
    async def on_message(message):
        await common_handle_message(message)
        await common_watcher_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    client.run(token)

###############################################################################


async def send_webhook(message):
    await webhook_helper.send_webhook(message, this.TEST_MODE)


if __name__ == "__main__":
    main(sys.argv[1:])
