import settings

from commands.base_command import BaseCommand

from helpers import common as common_helper
from helpers import errors as errors_helper
from helpers import db as db_helper


class Create_ticket_monitor(BaseCommand):

    def __init__(self):
        description = "Create new ticket watcher channel"
        params = ['marketplace']
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.guild.id not in settings.MACHETE_SERVER:
            return

        marketplace_param = common_helper.get_param_by_index(params, 0)
        if marketplace_param == 'all':
            marketplaces = settings.AVAILABLE_MARKETPLACES
        else:
            marketplaces = marketplace_param.split(',')

        for marketplace in marketplaces:
            if marketplace not in settings.AVAILABLE_MARKETPLACES:
                error = errors_helper.error_embed(
                    title='Unknown marketplace identifier',
                    description=f"Available marketplaces are **[{', '.join(settings.AVAILABLE_MARKETPLACES)}]**"
                )
                return await message.channel.send(embed=error)

        for marketplace in marketplaces:
            db = db_helper.mysql_get_mydb()
            inserted = db_helper.create_ticket_monitor(db, marketplace, message.guild.id, message.channel.id)
            if inserted:
                await message.channel.send(f":white_check_mark: {marketplace} ticket monitor added.")
