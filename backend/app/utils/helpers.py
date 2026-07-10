import json
import re


def truncate(text: str, max_len: int = 100) -> str:
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def safe_json_parse(text: str) -> dict | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def mask_sensitive(value: str, show: int = 4) -> str:
    if len(value) <= show:
        return "*" * len(value)
    return "*" * (len(value) - show) + value[-show:]


def extract_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
