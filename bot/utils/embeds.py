from __future__ import annotations

import discord


def auction_embed(title: str, description: str | None = None, color: discord.Color | None = None):
    return discord.Embed(title=title, description=description, color=color or discord.Color.blurple())