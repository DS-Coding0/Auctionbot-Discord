from discord.ext import tasks

from bot.services.auction_service import AuctionService


class AuctionLoops:
    def __init__(self, bot):
        self.bot = bot
        self.service = AuctionService()

    @tasks.loop(seconds=30)
    async def watch_auctions(self):
        self.service.close_due_auctions()

    @watch_auctions.before_loop
    async def before_watch_auctions(self):
        await self.bot.wait_until_ready()