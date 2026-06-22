from discord.ext import commands


def is_admin():
    return commands.has_permissions(administrator=True)


def is_owner():
    return commands.is_owner()


def guild_only():
    return commands.guild_only()