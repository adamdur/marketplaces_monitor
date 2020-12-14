import settings


help_message = f"**GENERAL TIPS**\n" \
               f"Add word **guide** as first parameter to any command to see guide for specific command \n" \
               f"Example: \n" \
               f"> **{settings.COMMAND_PREFIX}activity guide** - this will show guide for activity command \n" \
               f"> **{settings.COMMAND_PREFIX}demand guide** - this will show guide for demand command \n\n" \
               f"Add word **help** as first parameter to any command to see required/optional parameters for specific command \n" \
               f"Example: \n" \
               f"> **{settings.COMMAND_PREFIX}activity help** - this will show what parameters you need to add for activity command \n" \
               f"> **{settings.COMMAND_PREFIX}demand help** - this will show what parameters you need to add for demand command \n\n\n" \
               f"**USEFUL COMMANDS**\n" \
               f"> **{settings.COMMAND_PREFIX}help** - shows help message \n" \
               f"> **{settings.COMMAND_PREFIX}guide** - shows general guide \n" \
               f"> **{settings.COMMAND_PREFIX}commands** - shows all available commands \n\n\n"

guide = settings.COMMANDS_GUIDE_URL
