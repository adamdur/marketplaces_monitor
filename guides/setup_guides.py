import settings


help_message = f"**GENERAL TIPS**\n" \
               f"Add word **guide** as first parameter to any command to see guide for specific command \n" \
               f"Example: \n" \
               f"> **{settings.COMMAND_PREFIX}create guide** - this will show guide for creating monitor channels \n" \
               f"> **{settings.COMMAND_PREFIX}pings guide** - this will show guide for creating pings for monitor channels \n\n" \
               f"Add word **help** as first parameter to any command to see required/optional parameters for specific command \n" \
               f"Example: \n" \
               f"> **{settings.COMMAND_PREFIX}create help** - this will show what parameters you need to add for creating monitor channels \n" \
               f"> **{settings.COMMAND_PREFIX}ping_add help** - this will show what parameters you need to add for creating pings for monitor channels \n\n\n" \
               f"**USEFUL COMMANDS**\n" \
               f"> **{settings.COMMAND_PREFIX}help** - shows help message \n" \
               f"> **{settings.COMMAND_PREFIX}guide** - shows general guide \n" \
               f"> **{settings.COMMAND_PREFIX}commands** - shows all available commands \n\n\n"

guide = settings.SETUP_GUIDE_URL
