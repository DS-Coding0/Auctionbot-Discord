from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def utcnow():
    return datetime.now(ZoneInfo("Europe/Berlin"))


def to_iso(dt: datetime | None):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Europe/Berlin"))
    return dt.isoformat()