
class BaseCommandDm:
    def __init__(self, description, params, params_optional=None, guide=None):
        if params_optional is None:
            params_optional = []
        self.name = type(self).__name__.lower()
        self.params = params
        self.params_optional = params_optional
        self.description = description
        self.guide = guide

    async def handle(self, params, params_optional, message, client):
        raise NotImplementedError
