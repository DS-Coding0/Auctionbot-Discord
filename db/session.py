import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/auctionbot",
)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def init_models():
    from . import models as _models

    print("DATABASE_URL =", DATABASE_URL)
    print("TABLES =", list(Base.metadata.tables.keys()))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_engine():
    await engine.dispose()