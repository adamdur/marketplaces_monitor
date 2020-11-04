import sys
import os
import json
import emoji

import settings
import discord

from price_parser import Price
import re

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

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        if text.startswith(settings.COMMAND_PREFIX) and text != settings.COMMAND_PREFIX:
            if not [role for role in message.author.roles if role.name.lower() in settings.ALLOWED_ROLES]:
                return await message.channel.send(':no_entry: ' + message.author.mention + ' You are not allowed to use this command! :no_entry:')

            cmd_split = text[len(settings.COMMAND_PREFIX):].split()
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
            # embed_dict = {'footer': {'text': '[Splash Market]', 'proxy_icon_url': 'https://images-ext-1.discordapp.net/external/08sKcFl6UjQFshrFYYDmyFUehjTvlCzSE1e9JpgmFaw/%3Fq%3Dtbn%253AANd9GcTobiQybVGDOr_cpv9OaKlUOfq_PEEJy5J5fw%26usqp%3DCAU/https/encrypted-tbn0.gstatic.com/images', 'icon_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTobiQybVGDOr_cpv9OaKlUOfq_PEEJy5J5fw&usqp=CAU'}, 'thumbnail': {'width': 0, 'url': 'https://cdn.discordapp.com/icons/697351027728318495/111d140b7af11faa4b4f89e00ea41348.webp?size=1024', 'proxy_url': 'https://images-ext-2.discordapp.net/external/Jgb9DxJJehTJ8jwzvVyHYO5moPavCzQCQnMusuHmQJ0/%3Fsize%3D1024/https/cdn.discordapp.com/icons/697351027728318495/111d140b7af11faa4b4f89e00ea41348.webp', 'height': 0}, 'author': {'proxy_icon_url': 'https://images-ext-2.discordapp.net/external/Jgb9DxJJehTJ8jwzvVyHYO5moPavCzQCQnMusuHmQJ0/%3Fsize%3D1024/https/cdn.discordapp.com/icons/697351027728318495/111d140b7af11faa4b4f89e00ea41348.webp', 'name': 'Splash Market', 'icon_url': 'https://cdn.discordapp.com/icons/697351027728318495/111d140b7af11faa4b4f89e00ea41348.webp?size=1024'}, 'fields': [{'value': '1200$', 'name': 'Matched price:', 'inline': True}, {'value': '<@757934001305682021>', 'name': 'Posted by:', 'inline': True}, {'value': '<#759444386257305620>', 'name': 'Posted in:', 'inline': True}, {'value': ':link: **[VIEW ORIGINAL MESSAGE](https://discord.com/channels/697351027728318495/759444386257305620/773441658213236737)**', 'name': 'Message link:', 'inline': False}, {'value': '>>> WTR sieupreme LT 1200$', 'name': 'Message content:', 'inline': False}, {'value': '[MARKETPLACES MONITOR BY _SMYB#4736](https://adamduris.com)', 'name': '\u200b', 'inline': True}], 'color': 333, 'timestamp': '2020-11-04T07:01:01.169000+00:00', 'type': 'rich', 'title': 'New post in #wtro-backdoorio'}
            message_channel = embed_dict['title'].split("#")[1]

            message_content = ''
            for field in embed_dict['fields']:
                if field['name'] == 'Message content:':
                    message_content = field['value']

            final_types = common_helper.get_channel_types(message_channel, message_content)
            if not final_types:
                print('No type found: {}'.format(message_channel))
                return False
            # final_types = []
            # if any(s in message_channel for s in ['wtro', 'wtr', 'rental', 'rent', 'rental-sell']):
            #     if 'wtr ' in message_content.lower():
            #         final_types.append('wtr')
            #     if 'wtro' in message_content.lower():
            #         final_types.append('wtro')
            #     if not any(s in message_channel for s in ['wtr ', 'wtro']):
            #         final_types.append('wtro')
            # if not final_types:
            #     if any(s in message_channel for s in ['wts', 'sell']):
            #         final_types.append('wts')
            #     if any(s in message_channel for s in ['wtb', 'buy', 'wtt', 'trade']):
            #         if 'wtt' in message_content.lower():
            #             final_types.append('wtt')
            #         if 'wtb' in message_content.lower():
            #             final_types.append('wtb')
            #         if not any(s in message_channel for s in ['wtt', 'wtb']):
            #             final_types.append('wtb')
            #     if not final_types:
            #         print('No type found: {}'.format(message_channel))
            #         return

            # final_bot = ''
            # for bot in settings.ALLOWED_BOTS:
            #     aliases = settings.ALLOWED_BOTS[bot]
            #     if any(alias in message_channel for alias in aliases):
            #         final_bot = bot
            #         break

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

                        print('GOING TO POST IN {}'.format(final_channel))
                        await channel_to_post.send(embed=embed)
                        # await channel_to_post.send(message.content)

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
