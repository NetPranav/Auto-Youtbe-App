from datetime import datetime, timezone

def get_utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

def format_iso(dt: datetime) -> str:
    """Formats a datetime to an ISO 8601 string."""
    return dt.isoformat()
