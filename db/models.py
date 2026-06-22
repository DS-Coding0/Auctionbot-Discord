from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from .session import Base


class Server(Base):
    __tablename__ = 'servers'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(String(64), unique=True, nullable=False)
    username = Column(String(255), nullable=False)
    global_name = Column(String(255))
    avatar = Column(String(255))
    role = Column(String(32), nullable=False, default='buyer')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Show(Base):
    __tablename__ = 'shows'
    id = Column(BigInteger, primary_key=True)
    server_id = Column(BigInteger, ForeignKey('servers.id'), nullable=False)
    seller_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(32), nullable=False, default='draft')
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Item(Base):
    __tablename__ = 'items'
    id = Column(BigInteger, primary_key=True)
    show_id = Column(BigInteger, ForeignKey('shows.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(1024))
    start_price = Column(Numeric(10, 2), nullable=False, default=0)
    instant_buy_price = Column(Numeric(10, 2))
    min_increment = Column(Numeric(10, 2), nullable=False, default=1)
    status = Column(String(32), nullable=False, default='draft')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(BigInteger, primary_key=True)
    show_id = Column(BigInteger, ForeignKey('shows.id'), nullable=False)
    item_id = Column(BigInteger, ForeignKey('items.id'), nullable=False)
    channel_id = Column(String(64))
    message_id = Column(String(64))
    current_price = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(32), nullable=False, default='scheduled')
    ends_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(BigInteger, primary_key=True)
    buyer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    seller_id = Column(BigInteger, ForeignKey('users.id'))
    item_id = Column(BigInteger, ForeignKey('items.id'), nullable=False)
    auction_id = Column(BigInteger, ForeignKey('auctions.id'))
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(32), nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(BigInteger, primary_key=True)
    type = Column(String(64), nullable=False)
    entity_type = Column(String(64))
    entity_id = Column(String(64))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)