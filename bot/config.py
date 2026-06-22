import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    if value is None or value == '':
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    token: str = os.getenv('DISCORD_TOKEN', '')
    client_id: str = os.getenv('DISCORD_CLIENT_ID', '')
    client_secret: str = os.getenv('DISCORD_CLIENT_SECRET', '')
    public_key: str = os.getenv('DISCORD_PUBLIC_KEY', '')
    guild_id: int | None = _env_int('DISCORD_GUILD_ID')
    database_url: str = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/auctiobot')
    client_url: str = os.getenv('CLIENT_URL', 'http://localhost:5173')
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    command_prefix: str = os.getenv('COMMAND_PREFIX', '!')
    min_bid_increment: int = _env_int('MIN_BID_INCREMENT', 1) or 1
    instant_buy_enabled: bool = os.getenv('INSTANT_BUY_ENABLED', 'true').lower() in {'1', 'true', 'yes', 'on'}


config = Config()