import asyncio
import logging

from bot.client import BotClient
from bot.config import config


def setup_logging():
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def main():
    setup_logging()

    if not config.token:
        raise RuntimeError("DISCORD_TOKEN is missing")

    bot = BotClient()
    async with bot:
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())