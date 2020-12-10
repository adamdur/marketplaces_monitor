
class BaseCommand:
    def __init__(self, description, params, params_optional=None):
        if params_optional is None:
            params_optional = []
        self.name = type(self).__name__.lower()
        self.params = params
        self.params_optional = params_optional
        self.description = description

    async def handle(self, params, params_optional, message, client):
        raise NotImplementedError
