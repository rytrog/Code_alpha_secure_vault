from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime) -> str:
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return ""


def time_ago(dt: datetime) -> str:
    if not dt:
        return "unknown"
    diff = utcnow() - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return f"{seconds}s ago"
    elif seconds < 3600:
        return f"{seconds // 60}m ago"
    elif seconds < 86400:
        return f"{seconds // 3600}h ago"
    else:
        return f"{seconds // 86400}d ago"
