from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)


def to_iso(dt: datetime | None):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()