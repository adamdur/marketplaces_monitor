import settings

from commands.base_command import BaseCommand

from helpers import common as common_helper
from helpers import errors as errors_helper


class Bot(BaseCommand):

    def __init__(self):
        description = "Shows bot info"
        params = ['bot']
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if not message.guild.id == settings.MACHETE_SERVER:
            return

        bot = common_helper.get_param_by_index(params, 0)
        bot_data = await errors_helper.check_info_bot(bot, message.channel, guide=self.guide)
        if not bot_data:
            return

        try:
            channel = message.guild.get_channel(int(bot_data['channel_id']))
            info_message = await channel.fetch_message(bot_data['message_id'])
            embed = info_message.embeds[0]
        except:
            embed = errors_helper.error_embed()
            await message.channel.send(embed=embed)
            return

        await message.channel.send(embed=embed)
