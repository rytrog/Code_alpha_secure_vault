from functools import wraps
from fastapi import HTTPException, status
from ..constants import ROLE_ADMIN


def require_role(allowed_roles: list[str]):
    """Dependency-style role checker."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def is_admin(user) -> bool:
    return user and user.role == ROLE_ADMIN
