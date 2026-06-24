from bot.config import config
from bot.repositories.auction_repository import AuctionRepository
from bot.utils.time import utcnow


class AuctionService:
    def __init__(self, repo: AuctionRepository | None = None):
        self.repo = repo or AuctionRepository()

    async def list_auctions(self, show_id: int | None = None, status: str | None = None):
        return await self.repo.list_auctions(show_id=show_id, status=status)

    async def create_auction(
        self,
        show_id: int,
        item_id: int,
        current_price: float = 0,
        status: str = "scheduled",
        channel_id: str | None = None,
        message_id: str | None = None,
        ends_at=None,
    ):
        return await self.repo.create_auction(
            show_id=show_id,
            item_id=item_id,
            current_price=current_price,
            status=status,
            channel_id=channel_id,
            message_id=message_id,
            ends_at=ends_at,
        )

    async def get_auction(self, auction_id: int):
        return await self.repo.get_auction(auction_id)

    async def get_auction_context(self, auction_id: int):
        auction, item = await self.repo.get_auction_with_item(auction_id)
        if not auction:
            return None, None, None, "Auction not found"

        show = await self.repo.get_show(auction.show_id)
        return auction, item, show, None

    async def start_auction(self, auction_id: int):
        auction, item, show, error = await self.get_auction_context(auction_id)
        if error:
            return None, None, None, error

        if getattr(auction, "status", None) == "live":
            return auction, item, show, None

        update_data = {"status": "live"}

        if item is not None:
            start_price = getattr(item, "start_price", None)
            if start_price is not None and float(getattr(auction, "current_price", 0) or 0) <= 0:
                update_data["current_price"] = float(start_price)

        if getattr(auction, "ends_at", None) is None and getattr(show, "ends_at", None) is not None:
            update_data["ends_at"] = getattr(show, "ends_at")

        updated = await self.repo.update_auction(auction_id, **update_data)
        return updated, item, show, None

    async def end_auction(self, auction_id: int):
        return await self.repo.update_auction(auction_id, status="ended")

    async def list_live_auctions(self):
        return await self.repo.list_auctions(status="live")

    async def bid(
        self,
        auction_id: int,
        buyer_id: int,
        amount: float,
        min_increment: float | None = None,
        seller_id: int | None = None,
    ):
        auction = await self.get_auction(auction_id)
        if not auction:
            return None, "Auction not found"

        if auction.status != "live":
            return None, "Auction is not live"

        item = await self.repo.get_item(auction.item_id)
        show = await self.repo.get_show(auction.show_id)

        seller_id = seller_id or getattr(show, "seller_id", None)
        if seller_id is not None and seller_id == buyer_id:
            return None, "Seller cannot bid on own auction"

        increment = (
            float(min_increment)
            if min_increment is not None
            else float(getattr(item, "min_increment", config.min_bid_increment))
        )
        required = float(auction.current_price or 0) + increment
        if amount < required:
            return None, f"Minimum bid is {required}"

        updated = await self.repo.place_bid(
            auction_id=auction_id,
            buyer_id=buyer_id,
            amount=amount,
        )
        return updated, None

    async def instant_buy(self, auction_id: int, buyer_id: int):
        if not config.instant_buy_enabled:
            return None, "Instant buy is disabled"

        auction, item = await self.repo.get_auction_with_item(auction_id)
        if not auction or not item:
            return None, "Auction or item not found"

        show = await self.repo.get_show(auction.show_id)
        seller_id = getattr(show, "seller_id", None)

        if seller_id is not None and seller_id == buyer_id:
            return None, "Seller cannot buy own auction"

        if getattr(item, "instant_buy_price", None) is None:
            return None, "Instant buy not available"

        auction = await self.repo.finish_with_instant_buy(
            auction_id=auction_id,
            buyer_id=buyer_id,
            amount=float(item.instant_buy_price),
        )

        order = await self.repo.create_order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            item_id=item.id,
            auction_id=auction_id,
            quantity=1,
            total_price=float(item.instant_buy_price),
            status="completed",
        )
        return {"auction": auction, "order": order}, None

    async def close_due_auctions(self):
        closed = []
        auctions = await self.list_live_auctions()
        for auction in auctions:
            if auction.ends_at and auction.ends_at <= utcnow():
                closed.append(await self.end_auction(auction.id))
        return closed

    async def close(self):
        await self.repo.close()