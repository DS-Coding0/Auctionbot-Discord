import discord


def base_embed(title: str, description: str | None = None, color: int = 0x5865F2):
    return discord.Embed(title=title, description=description, color=color)


def success_embed(title: str, description: str | None = None):
    return base_embed(title, description, color=0x57F287)


def error_embed(title: str, description: str | None = None):
    return base_embed(title, description, color=0xED4245)