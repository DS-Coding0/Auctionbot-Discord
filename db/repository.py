from __future__ import annotations

from typing import Optional, Iterable
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func

from .session import SessionLocal
from .models import (
    Server,
    User,
    Show,
    Item,
    Auction,
    Order,
    Rating,
    SellerBannedBuyer,
    AuditLog,
)


class Repository:
    def __init__(self, db: Session | None = None):
        self.db = db or SessionLocal()

    def close(self):
        self.db.close()

    def commit(self):
        self.db.commit()

    def refresh(self, obj):
        self.db.refresh(obj)
        return obj

    def add(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.commit()

    def get_server(self, server_id: int) -> Optional[Server]:
        return self.db.get(Server, server_id)

    def get_or_create_server(self, server_id: int, name: str) -> Server:
        server = self.get_server(server_id)
        if server:
            if name and server.name != name:
                server.name = name
                self.db.commit()
                self.db.refresh(server)
            return server
        server = Server(id=server_id, name=name)
        return self.add(server)

    def get_user_by_discord_id(self, discord_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.discord_id == discord_id).first()

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_or_create_user(
        self,
        discord_id: str,
        username: str,
        global_name: str | None = None,
        avatar: str | None = None,
        role: str = 'buyer',
    ) -> User:
        user = self.get_user_by_discord_id(discord_id)
        if user:
            user.username = username or user.username
            user.global_name = global_name
            user.avatar = avatar
            user.role = role or user.role
            self.db.commit()
            self.db.refresh(user)
            return user
        user = User(discord_id=discord_id, username=username, global_name=global_name, avatar=avatar, role=role)
        return self.add(user)

    def list_shows(self, server_id: int | None = None, seller_id: int | None = None, status: str | None = None) -> list[Show]:
        q = self.db.query(Show)
        if server_id is not None:
            q = q.filter(Show.server_id == server_id)
        if seller_id is not None:
            q = q.filter(Show.seller_id == seller_id)
        if status is not None:
            q = q.filter(Show.status == status)
        return q.order_by(Show.created_at.desc()).all()

    def get_show(self, show_id: int) -> Optional[Show]:
        return self.db.get(Show, show_id)

    def create_show(self, **kwargs) -> Show:
        return self.add(Show(**kwargs))

    def update_show(self, show_id: int, **kwargs) -> Optional[Show]:
        show = self.get_show(show_id)
        if not show:
            return None
        for key, value in kwargs.items():
            if hasattr(show, key):
                setattr(show, key, value)
        self.db.commit()
        self.db.refresh(show)
        return show

    def delete_show(self, show_id: int) -> bool:
        show = self.get_show(show_id)
        if not show:
            return False
        self.delete(show)
        return True

    def list_items(self, show_id: int | None = None, status: str | None = None) -> list[Item]:
        q = self.db.query(Item)
        if show_id is not None:
            q = q.filter(Item.show_id == show_id)
        if status is not None:
            q = q.filter(Item.status == status)
        return q.order_by(Item.created_at.desc()).all()

    def get_item(self, item_id: int) -> Optional[Item]:
        return self.db.get(Item, item_id)

    def create_item(self, **kwargs) -> Item:
        return self.add(Item(**kwargs))

    def update_item(self, item_id: int, **kwargs) -> Optional[Item]:
        item = self.get_item(item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        item = self.get_item(item_id)
        if not item:
            return False
        self.delete(item)
        return True

    def list_auctions(self, show_id: int | None = None, status: str | None = None) -> list[Auction]:
        q = self.db.query(Auction)
        if show_id is not None:
            q = q.filter(Auction.show_id == show_id)
        if status is not None:
            q = q.filter(Auction.status == status)
        return q.order_by(Auction.created_at.desc()).all()

    def get_auction(self, auction_id: int) -> Optional[Auction]:
        return self.db.get(Auction, auction_id)

    def create_auction(self, **kwargs) -> Auction:
        return self.add(Auction(**kwargs))

    def update_auction(self, auction_id: int, **kwargs) -> Optional[Auction]:
        auction = self.get_auction(auction_id)
        if not auction:
            return None
        for key, value in kwargs.items():
            if hasattr(auction, key):
                setattr(auction, key, value)
        self.db.commit()
        self.db.refresh(auction)
        return auction

    def delete_auction(self, auction_id: int) -> bool:
        auction = self.get_auction(auction_id)
        if not auction:
            return False
        self.delete(auction)
        return True

    def list_orders(self, buyer_id: int | None = None, seller_id: int | None = None, status: str | None = None) -> list[Order]:
        q = self.db.query(Order)
        if buyer_id is not None:
            q = q.filter(Order.buyer_id == buyer_id)
        if seller_id is not None:
            q = q.filter(Order.seller_id == seller_id)
        if status is not None:
            q = q.filter(Order.status == status)
        return q.order_by(Order.created_at.desc()).all()

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.db.get(Order, order_id)

    def create_order(self, **kwargs) -> Order:
        return self.add(Order(**kwargs))

    def update_order(self, order_id: int, **kwargs) -> Optional[Order]:
        order = self.get_order(order_id)
        if not order:
            return None
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete_order(self, order_id: int) -> bool:
        order = self.get_order(order_id)
        if not order:
            return False
        self.delete(order)
        return True

    def list_ratings(self, target_user_id: int | None = None, rater_id: int | None = None, show_id: int | None = None) -> list[Rating]:
        q = self.db.query(Rating)
        if target_user_id is not None:
            q = q.filter(Rating.target_user_id == target_user_id)
        if rater_id is not None:
            q = q.filter(Rating.rater_id == rater_id)
        if show_id is not None:
            q = q.filter(Rating.show_id == show_id)
        return q.order_by(Rating.created_at.desc()).all()

    def create_rating(self, **kwargs) -> Rating:
        rating = Rating(**kwargs)
        return self.add(rating)

    def get_ban(self, seller_id: int, buyer_id: int) -> Optional[SellerBannedBuyer]:
        return self.db.query(SellerBannedBuyer).filter(
            SellerBannedBuyer.seller_id == seller_id,
            SellerBannedBuyer.buyer_id == buyer_id,
        ).first()

    def is_buyer_banned(self, seller_id: int, buyer_id: int) -> bool:
        ban = self.db.query(SellerBannedBuyer).filter(
            SellerBannedBuyer.seller_id == seller_id,
            SellerBannedBuyer.buyer_id == buyer_id,
            SellerBannedBuyer.active.is_(True),
        ).first()
        return ban is not None

    def upsert_ban(self, seller_id: int, buyer_id: int, reason: str | None = None, active: bool = True) -> SellerBannedBuyer:
        ban = self.get_ban(seller_id, buyer_id)
        if ban:
            ban.reason = reason
            ban.active = active
            self.db.commit()
            self.db.refresh(ban)
            return ban
        ban = SellerBannedBuyer(seller_id=seller_id, buyer_id=buyer_id, reason=reason, active=active)
        return self.add(ban)

    def list_bans(self, seller_id: int | None = None, active: bool | None = None) -> list[SellerBannedBuyer]:
        q = self.db.query(SellerBannedBuyer)
        if seller_id is not None:
            q = q.filter(SellerBannedBuyer.seller_id == seller_id)
        if active is not None:
            q = q.filter(SellerBannedBuyer.active == active)
        return q.order_by(SellerBannedBuyer.created_at.desc()).all()

    def create_log(self, **kwargs) -> AuditLog:
        return self.add(AuditLog(**kwargs))