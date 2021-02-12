from commands_dm.base_command_dm import BaseCommandDm as BaseCommand

from helpers import db as db_helper
from helpers import common as common_helper


class Add_info(BaseCommand):

    def __init__(self):
        description = "Add bot guide message"
        params = ['bot', 'message_id']
        params_optional = ['channel_id']
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        bot = common_helper.get_param_by_index(params, 0)
        message_id = common_helper.get_param_by_index(params, 1)
        channel_id = common_helper.get_optional_param_by_index(params_optional, 0)

        db = db_helper.mysql_get_mydb()
        bot_info = db_helper.add_info(db, bot, message_id, channel_id)
        if not bot_info:
            return

        await message.author.send("Inserted...")
