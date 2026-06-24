from discord.ext import tasks

from bot.services.auction_service import AuctionService


class AuctionLoops:
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=30)
    async def watch_auctions(self):
        service = AuctionService()
        try:
            await service.close_due_auctions()
        finally:
            await service.close()

    @watch_auctions.before_loop
    async def before_watch_auctions(self):
        await self.bot.wait_until_ready()