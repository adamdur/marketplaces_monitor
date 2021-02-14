import settings

from commands.base_command import BaseCommand

from helpers import db as db_helper


class Destroy_ticket_monitor(BaseCommand):

    def __init__(self):
        description = "Destroy new ticket watcher channel"
        params = []
        params_optional = []
        guide = ''
        super().__init__(description, params, params_optional, guide)

    async def handle(self, params, params_optional, message, client):
        if message.guild.id not in settings.MACHETE_SERVER:
            return

        db = db_helper.mysql_get_mydb()
        destroyed = db_helper.destroy_ticket_monitor(db, message.guild.id, message.channel.id)
        if destroyed:
            await message.channel.send(f":white_check_mark: Ticket monitor destroyed.")