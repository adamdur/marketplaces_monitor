import settings
import discord


def get_role(roles, role_name):
    return discord.utils.get(roles, name=role_name)


def get_allowed_roles(roles):
    allowed_roles = []
    for role in roles:
        if role.name.lower() in settings.ALLOWED_ROLES:
            role = get_role(roles, role.name)
            if role:
                allowed_roles.append(role)

    return allowed_roles
