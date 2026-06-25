from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Auction,
    AuditLog,
    Item,
    Order,
    Rating,
    SellerBannedBuyer,
    Server,
    Show,
    User,
)
from .session import AsyncSessionLocal


class Repository:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db
        self._owns_session = db is None

    async def _get_db(self) -> AsyncSession:
        if self.db is None:
            self.db = AsyncSessionLocal()
        return self.db

    async def close(self):
        if self.db is not None and self._owns_session:
            await self.db.close()
            self.db = None

    async def commit(self):
        db = await self._get_db()
        await db.commit()

    async def refresh(self, obj):
        db = await self._get_db()
        await db.refresh(obj)
        return obj

    async def add(self, obj):
        db = await self._get_db()
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, obj):
        db = await self._get_db()
        await db.delete(obj)
        await db.commit()

    async def get_server(self, server_id: int) -> Server | None:
        db = await self._get_db()
        return await db.get(Server, server_id)

    async def get_or_create_server(self, server_id: int, name: str) -> Server:
        server = await self.get_server(server_id)
        if server:
            if name and server.name != name:
                server.name = name
                await self.commit()
                await self.refresh(server)
            return server

        return await self.add(Server(id=server_id, name=name))

    async def get_user_by_discord_id(self, discord_id: str) -> User | None:
        db = await self._get_db()
        stmt = select(User).where(User.discord_id == discord_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_user(self, user_id: int) -> User | None:
        db = await self._get_db()
        return await db.get(User, user_id)

    async def get_or_create_user(
        self,
        discord_id: str,
        username: str,
        global_name: str | None = None,
        avatar: str | None = None,
        role: str = "buyer",
    ) -> User:
        user = await self.get_user_by_discord_id(discord_id)
        if user:
            user.username = username or user.username
            user.global_name = global_name
            user.avatar = avatar
            user.role = role or user.role
            await self.commit()
            await self.refresh(user)
            return user

        return await self.add(
            User(
                discord_id=discord_id,
                username=username,
                global_name=global_name,
                avatar=avatar,
                role=role,
            )
        )

    async def list_shows(
        self,
        server_id: int | None = None,
        seller_id: int | None = None,
        status: str | None = None,
    ) -> list[Show]:
        db = await self._get_db()
        stmt = select(Show)

        if server_id is not None:
            stmt = stmt.where(Show.server_id == server_id)
        if seller_id is not None:
            stmt = stmt.where(Show.seller_id == seller_id)
        if status is not None:
            stmt = stmt.where(Show.status == status)

        stmt = stmt.order_by(Show.starts_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_show(self, show_id: int) -> Show | None:
        db = await self._get_db()
        return await db.get(Show, show_id)

    async def create_show(self, **kwargs) -> Show:
        return await self.add(Show(**kwargs))

    async def update_show(self, show_id: int, **kwargs) -> Show | None:
        show = await self.get_show(show_id)
        if not show:
            return None

        for key, value in kwargs.items():
            if hasattr(show, key):
                setattr(show, key, value)

        await self.commit()
        await self.refresh(show)
        return show

    async def delete_show(self, show_id: int) -> bool:
        show = await self.get_show(show_id)
        if not show:
            return False

        await self.delete(show)
        return True

    async def list_items(
        self,
        show_id: int | None = None,
        status: str | None = None,
    ) -> list[Item]:
        db = await self._get_db()
        stmt = select(Item)

        if show_id is not None:
            stmt = stmt.where(Item.show_id == show_id)
        if status is not None:
            stmt = stmt.where(Item.status == status)

        stmt = stmt.order_by(Item.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_item(self, item_id: int) -> Item | None:
        db = await self._get_db()
        return await db.get(Item, item_id)

    async def create_item(self, **kwargs) -> Item:
        return await self.add(Item(**kwargs))

    async def update_item(self, item_id: int, **kwargs) -> Item | None:
        item = await self.get_item(item_id)
        if not item:
            return None

        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)

        await self.commit()
        await self.refresh(item)
        return item

    async def delete_item(self, item_id: int) -> bool:
        item = await self.get_item(item_id)
        if not item:
            return False

        await self.delete(item)
        return True

    async def list_auctions(
        self,
        show_id: int | None = None,
        status: str | None = None,
    ) -> list[Auction]:
        db = await self._get_db()
        stmt = select(Auction)

        if show_id is not None:
            stmt = stmt.where(Auction.show_id == show_id)
        if status is not None:
            stmt = stmt.where(Auction.status == status)

        stmt = stmt.order_by(Auction.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_auction(self, auction_id: int) -> Auction | None:
        db = await self._get_db()
        return await db.get(Auction, auction_id)

    async def create_auction(self, **kwargs) -> Auction:
        return await self.add(Auction(**kwargs))

    async def update_auction(self, auction_id: int, **kwargs) -> Auction | None:
        auction = await self.get_auction(auction_id)
        if not auction:
            return None

        for key, value in kwargs.items():
            if hasattr(auction, key):
                setattr(auction, key, value)

        await self.commit()
        await self.refresh(auction)
        return auction

    async def delete_auction(self, auction_id: int) -> bool:
        auction = await self.get_auction(auction_id)
        if not auction:
            return False

        await self.delete(auction)
        return True

    async def list_orders(
        self,
        buyer_id: int | None = None,
        seller_id: int | None = None,
        status: str | None = None,
    ) -> list[Order]:
        db = await self._get_db()
        stmt = select(Order)

        if buyer_id is not None:
            stmt = stmt.where(Order.buyer_id == buyer_id)
        if seller_id is not None:
            stmt = stmt.where(Order.seller_id == seller_id)
        if status is not None:
            stmt = stmt.where(Order.status == status)

        stmt = stmt.order_by(Order.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_order(self, order_id: int) -> Order | None:
        db = await self._get_db()
        return await db.get(Order, order_id)

    async def create_order(self, **kwargs) -> Order:
        return await self.add(Order(**kwargs))

    async def update_order(self, order_id: int, **kwargs) -> Order | None:
        order = await self.get_order(order_id)
        if not order:
            return None

        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)

        await self.commit()
        await self.refresh(order)
        return order

    async def delete_order(self, order_id: int) -> bool:
        order = await self.get_order(order_id)
        if not order:
            return False

        await self.delete(order)
        return True

    async def list_ratings(
        self,
        target_user_id: int | None = None,
        rater_id: int | None = None,
        show_id: int | None = None,
    ) -> list[Rating]:
        db = await self._get_db()
        stmt = select(Rating)

        if target_user_id is not None:
            stmt = stmt.where(Rating.target_user_id == target_user_id)
        if rater_id is not None:
            stmt = stmt.where(Rating.rater_id == rater_id)
        if show_id is not None:
            stmt = stmt.where(Rating.show_id == show_id)

        stmt = stmt.order_by(Rating.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_rating(self, **kwargs) -> Rating:
        return await self.add(Rating(**kwargs))

    async def get_ban(self, seller_id: int, buyer_id: int) -> SellerBannedBuyer | None:
        db = await self._get_db()
        stmt = select(SellerBannedBuyer).where(
            SellerBannedBuyer.seller_id == seller_id,
            SellerBannedBuyer.buyer_id == buyer_id,
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def is_buyer_banned(self, seller_id: int, buyer_id: int) -> bool:
        db = await self._get_db()
        stmt = select(SellerBannedBuyer).where(
            SellerBannedBuyer.seller_id == seller_id,
            SellerBannedBuyer.buyer_id == buyer_id,
            SellerBannedBuyer.active.is_(True),
        )
        result = await db.execute(stmt)
        return result.scalars().first() is not None

    async def upsert_ban(
        self,
        seller_id: int,
        buyer_id: int,
        reason: str | None = None,
        active: bool = True,
    ) -> SellerBannedBuyer:
        ban = await self.get_ban(seller_id, buyer_id)
        if ban:
            ban.reason = reason
            ban.active = active
            await self.commit()
            await self.refresh(ban)
            return ban

        return await self.add(
            SellerBannedBuyer(
                seller_id=seller_id,
                buyer_id=buyer_id,
                reason=reason,
                active=active,
            )
        )

    async def list_bans(
        self,
        seller_id: int | None = None,
        active: bool | None = None,
    ) -> list[SellerBannedBuyer]:
        db = await self._get_db()
        stmt = select(SellerBannedBuyer)

        if seller_id is not None:
            stmt = stmt.where(SellerBannedBuyer.seller_id == seller_id)
        if active is not None:
            stmt = stmt.where(SellerBannedBuyer.active == active)

        stmt = stmt.order_by(SellerBannedBuyer.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_log(self, **kwargs) -> AuditLog:
        return await self.add(AuditLog(**kwargs))