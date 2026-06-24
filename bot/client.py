import discord
from discord.ext import commands

from bot.config import config
from bot.tasks.auction_loops import AuctionLoops


class BotClient(commands.Bot):
    def __init__(self, **kwargs):
        intents = kwargs.pop("intents", discord.Intents.default())
        command_prefix = kwargs.pop(
            "command_prefix",
            config.command_prefix if hasattr(config, "command_prefix") else "!",
        )

        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
        self.auction_loops = AuctionLoops(self)

    async def setup_hook(self):
        await self.load_extension("bot.cogs.auctions")
        await self.load_extension("bot.cogs.items")
        await self.load_extension("bot.cogs.admin")
        await self.load_extension("bot.cogs.orders")
        await self.load_extension("bot.cogs.ratings")
        await self.load_extension("bot.cogs.registration")
        await self.load_extension("bot.cogs.shows")

        if not self.auction_loops.watch_auctions.is_running():
            self.auction_loops.watch_auctions.start()

        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")