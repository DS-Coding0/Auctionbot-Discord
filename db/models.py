from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from .session import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    discord_id = Column(String(64), unique=True, nullable=False)
    username = Column(String(255), nullable=False)
    global_name = Column(String(255))
    avatar = Column(String(1024))
    role = Column(String(32), nullable=False, default="buyer")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_users_discord_id", "discord_id"),
    )


class Show(Base):
    __tablename__ = "shows"

    id = Column(BigInteger, primary_key=True)
    server_id = Column(BigInteger, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(32), nullable=False, default="draft")
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    voice_channel_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_shows_server_id", "server_id"),
        Index("idx_shows_seller_id", "seller_id"),
        Index("idx_shows_status", "status"),
    )


class Item(Base):
    __tablename__ = "items"

    id = Column(BigInteger, primary_key=True)
    show_id = Column(BigInteger, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(1024))
    start_price = Column(Numeric(10, 2), nullable=False, default=0)
    instant_buy_price = Column(Numeric(10, 2))
    min_increment = Column(Numeric(10, 2), nullable=False, default=1)
    status = Column(String(32), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("start_price >= 0", name="items_start_price_nonnegative"),
        CheckConstraint(
            "instant_buy_price IS NULL OR instant_buy_price >= 0",
            name="items_instant_buy_price_nonnegative",
        ),
        CheckConstraint("min_increment > 0", name="items_min_increment_positive"),
        CheckConstraint(
            "instant_buy_price IS NULL OR instant_buy_price >= start_price",
            name="items_instant_buy_ge_start",
        ),
        Index("idx_items_show_id", "show_id"),
        Index("idx_items_status", "status"),
    )


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(BigInteger, primary_key=True)
    show_id = Column(BigInteger, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(BigInteger, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, unique=True)
    channel_id = Column(String(64))
    message_id = Column(String(64))
    current_price = Column(Numeric(10, 2), nullable=False, default=0)
    highest_bidder_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    status = Column(String(32), nullable=False, default="scheduled")
    ends_at = Column(DateTime(timezone=True))
    highest_bidder_id = Column(BigInteger, ForeignKey("users.id"))
    reset_seconds = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("current_price >= 0", name="auctions_current_price_nonnegative"),
        Index("idx_auctions_show_id", "show_id"),
        Index("idx_auctions_status", "status"),
        Index("idx_auctions_ends_at", "ends_at"),
        Index("idx_auctions_highest_bidder_id", "highest_bidder_id"),
    )


class Bid(Base):
    __tablename__ = "bids"

    id = Column(BigInteger, primary_key=True)
    auction_id = Column(BigInteger, ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="bids_amount_positive"),
        Index("idx_bids_auction_id", "auction_id"),
        Index("idx_bids_buyer_id", "buyer_id"),
        Index("idx_bids_auction_amount_created", "auction_id", "amount", "created_at"),
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True)
    buyer_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    seller_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    item_id = Column(BigInteger, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    auction_id = Column(BigInteger, ForeignKey("auctions.id", ondelete="SET NULL"))
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="orders_quantity_positive"),
        CheckConstraint("total_price >= 0", name="orders_total_price_nonnegative"),
        Index("idx_orders_buyer_id", "buyer_id"),
        Index("idx_orders_seller_id", "seller_id"),
        Index("idx_orders_item_id", "item_id"),
        Index("idx_orders_auction_id", "auction_id"),
        Index("idx_orders_status", "status"),
    )


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(BigInteger, primary_key=True)
    show_id = Column(BigInteger, ForeignKey("shows.id", ondelete="CASCADE"))
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="SET NULL"))
    rater_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("score BETWEEN 1 AND 5", name="ratings_score_between_1_and_5"),
        UniqueConstraint("order_id", "rater_id", name="ratings_unique_per_order"),
        Index("idx_ratings_target_user_id", "target_user_id"),
        Index("idx_ratings_rater_id", "rater_id"),
        Index("idx_ratings_order_id", "order_id"),
    )


class SellerBannedBuyer(Base):
    __tablename__ = "seller_banned_buyers"

    id = Column(BigInteger, primary_key=True)
    seller_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("seller_id", "buyer_id", name="seller_banned_buyers_unique"),
        Index("idx_seller_banned_buyers_seller_active", "seller_id", "active"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True)
    type = Column(String(64), nullable=False)
    entity_type = Column(String(64))
    entity_id = Column(String(64))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_audit_logs_type", "type"),
        Index("idx_audit_logs_entity", "entity_type", "entity_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    )