from __future__ import annotations

from sqlalchemy import select

from db.models import Auction, Bid, Item
from db.repository import Repository


class AuctionRepository(Repository):
    async def get_auction_with_item(self, auction_id: int) -> tuple[Auction | None, Item | None]:
        auction = await self.get_auction(auction_id)
        if not auction:
            return None, None

        item = await self.get_item(auction.item_id)
        return auction, item

    async def list_live_auctions(self) -> list[Auction]:
        return await self.list_auctions(status="live")

    async def update_price(
        self,
        auction_id: int,
        price: float,
        status: str | None = None,
        highest_bidder_id: int | None = None,
        ends_at=None,
    ) -> Auction | None:
        data = {
            "current_price": price,
        }

        if status is not None:
            data["status"] = status

        if highest_bidder_id is not None:
            data["highest_bidder_id"] = highest_bidder_id

        if ends_at is not None:
            data["ends_at"] = ends_at

        return await self.update_auction(auction_id, **data)

    async def create_bid(
        self,
        auction_id: int,
        buyer_id: int,
        amount: float,
    ) -> Bid:
        return await self.add(
            Bid(
                auction_id=auction_id,
                buyer_id=buyer_id,
                amount=amount,
            )
        )

    async def place_bid(
        self,
        auction_id: int,
        buyer_id: int,
        amount: float,
        ends_at=None,
    ) -> Auction | None:
        await self.create_bid(
            auction_id=auction_id,
            buyer_id=buyer_id,
            amount=amount,
        )

        return await self.update_price(
            auction_id=auction_id,
            price=amount,
            highest_bidder_id=buyer_id,
            ends_at=ends_at,
        )

    async def list_bids(self, auction_id: int) -> list[Bid]:
        db = await self._get_db()
        stmt = (
            select(Bid)
            .where(Bid.auction_id == auction_id)
            .order_by(Bid.amount.desc(), Bid.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_highest_bid(self, auction_id: int) -> Bid | None:
        db = await self._get_db()
        stmt = (
            select(Bid)
            .where(Bid.auction_id == auction_id)
            .order_by(Bid.amount.desc(), Bid.created_at.asc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalars().first()