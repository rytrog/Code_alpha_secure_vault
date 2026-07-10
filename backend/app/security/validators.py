import re
from fastapi import HTTPException, status


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    if len(username) < 3 or len(username) > 30:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def sanitize_input(value: str) -> str:
    """Remove potentially dangerous characters."""
    return re.sub(r'[<>"\';]', '', value).strip()


def validate_vault_category(category: str) -> bool:
    from ..constants import VAULT_CATEGORIES
    return category in VAULT_CATEGORIES


def require_non_empty(value: str, field_name: str):
    if not value or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot be empty"
        )
