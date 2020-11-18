import settings


class BaseCommand:
    def __init__(self, description, params, params_optional=None):
        if params_optional is None:
            params_optional = []
        self.name = type(self).__name__.lower()
        self.params = params
        self.params_optional = params_optional

        desc = f"**{settings.COMMAND_PREFIX}{self.name}**"

        if self.params:
            desc += " " + " ".join(f"*<{p}>*" for p in params)
        if self.params_optional:
            desc += " " + " ".join(f"*[{p}]*" for p in params_optional)

        desc += f"\n> {description}\n"
        self.description = desc

    async def handle(self, params, params_optional, message, client):
        raise NotImplementedError  # To be defined by every command
