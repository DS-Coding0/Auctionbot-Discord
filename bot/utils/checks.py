from __future__ import annotations

from discord.ext import commands


def is_owner():
    async def predicate(ctx_or_interaction):
        bot = getattr(ctx_or_interaction, 'bot', None) or getattr(getattr(ctx_or_interaction, 'client', None), 'bot', None)
        if bot is None:
            bot = getattr(ctx_or_interaction, 'client', None)
        app = bot or getattr(ctx_or_interaction, 'client', None)
        user = getattr(ctx_or_interaction, 'user', None) or getattr(ctx_or_interaction, 'author', None)
        if app is None or user is None:
            return False
        owner_ids = getattr(app, 'owner_ids', None)
        if owner_ids is not None:
            return user.id in owner_ids
        application = getattr(app, 'application', None)
        owner = getattr(application, 'owner', None) if application else None
        return owner is not None and user.id == owner.id
    return commands.check(predicate)