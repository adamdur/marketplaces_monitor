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


def main():
    print("Starting up...")
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
            this.setup_data.append(await guild_helper.base_guild_setup(guild))

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
        this.setup_data.append(await guild_helper.base_guild_setup(guild))

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
            for field in embed_dict['fields']:
                if field['name'] == 'Message content:':
                    message_content = field['value']

            final_types = common_helper.get_channel_types(message_channel, message_content)
            if not final_types:
                print('No type found: {}'.format(message_channel))
                return False

            final_bot = common_helper.get_bot_from_channel(message_channel)
            if not final_bot:
                print('Bot not found: {}'.format(message_channel))
                return

            final_channels = []
            if final_bot and final_types:
                for type in final_types:
                    final_channels.append("{}-{}".format(final_bot, type))

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

    @client.event
    async def on_message(message):
        await common_handle_message(message)
        await common_watcher_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # Finally, set the bot running
    client.run(settings.BOT_TOKEN)

###############################################################################


if __name__ == "__main__":
    main()
