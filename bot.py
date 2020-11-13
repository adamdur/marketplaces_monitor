import getopt
import sys
import settings
import discord

from handlers import message_handler
from helpers import guild as guild_helper
from helpers import common as common_helper
from helpers import setup_data as setup_data_helper
from helpers import channels as channels_helper

this = sys.modules[__name__]
this.running = False
this.setup_data = []


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
        for guild in client.guilds:
            if int(guild.id) in settings.VERIFIED_GUILDS:
                this.setup_data.append(await guild_helper.base_guild_setup(guild))
            else:
                await guild.leave()

        print("Everything set up... Watching marketplaces...")

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

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        if text.startswith(settings.COMMAND_PREFIX) and text != settings.COMMAND_PREFIX:
            cmd_split = text[len(settings.COMMAND_PREFIX):].split()
            if cmd_split[0].lower() in settings.ADMIN_COMMANDS:
                if not [role for role in message.author.roles if role.name.lower() in settings.ALLOWED_ROLES]:
                    return await message.channel.send(':no_entry: ' + message.author.mention + ' You are not allowed to use this command! :no_entry:')
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
                if field['name'] == 'Message content:':
                    message_content = field['value']
                elif field['name'] == 'Matched price:':
                    price_str = field['value']
                elif field['name'] == 'Price level:':
                    price_level = field['value']
                    remove_indexes.append(index)
                elif field['name'] == 'Is lifetime:':
                    is_lifetime = field['value']
                    remove_indexes.append(index)

            for remove_index in sorted(remove_indexes, key=int, reverse=True):
                embed.remove_field(remove_index)

            final_types = common_helper.get_channel_types(message_channel, message_content)
            if not final_types:
                print('No type found: {}'.format(message_channel))
                return False

            final_bot = common_helper.get_bot_from_channel(message_channel)
            if not final_bot:
                print('Bot not found: {}'.format(message_channel))
                return
            if final_bot in ['mek', 'mekpreme']:
                if any(x in message.content.lower() for x in ['mekaio', 'aio']):
                    final_bot = 'mekaio'

            final_channels = []
            notify = False
            if final_bot and final_types:
                for type in final_types:
                    final_channels.append("{}-{}".format(final_bot, type))
                    if price_level and price_str:
                        if type in ['wts', 'wtb'] and int(price_level) == 1:
                            message_data = common_helper.build_status_message(final_bot, price_str, type, is_lifetime)
                            embed.insert_field_at(5, name="Status:", value=message_data['message'], inline=False)
                            if message_data['notify'] is True:
                                notify = True

            for data in this.setup_data:
                guild_id = list(data)[0]
                setup = await setup_data_helper.get_data_by_id(guild_id)
                channels = setup['channels']
                channel_names = list(channels.keys())

                for final_channel in final_channels:
                    if final_channel in channel_names:
                        channel_id = channels[final_channel]

                        channel_to_post = channels_helper.get_channel_by_id(data[guild_id]['guild'].channels, channel_id)

                        print('---> GOING TO POST IN {}'.format(final_channel))
                        await channel_to_post.send(embed=embed)
                        if notify and settings.NOTIFY:
                            await channel_to_post.send(settings.NOTIFY_HANDLE)

    @client.event
    async def on_message(message):
        await common_handle_message(message)
        await common_watcher_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    client.run(token)

###############################################################################


if __name__ == "__main__":
    main(sys.argv[1:])
