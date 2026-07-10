from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..database import crud
from ..security.password import hash_password, verify_password, validate_password_strength
from ..security.jwt_handler import create_access_token
from ..security.validators import validate_email, validate_username
from ..utils.logger import auth_logger


def register_user(db: Session, username: str, email: str, password: str, ip: str = "unknown") -> dict:
    if not validate_username(username):
        raise HTTPException(status_code=400, detail="Invalid username. Use 3-30 alphanumeric characters or underscores.")

    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    valid, msg = validate_password_strength(password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    if crud.get_user_by_username(db, username):
        raise HTTPException(status_code=409, detail="Username already exists")

    if crud.get_user_by_email(db, email):
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(password)
    user = crud.create_user(db, username, email, hashed)
    auth_logger.info(f"User registered: {username} from {ip}")
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}


def login_user(db: Session, username: str, password: str, ip: str = "unknown") -> dict:
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        auth_logger.warning(f"Failed login attempt for '{username}' from {ip}")
        crud.create_login_log(db, username, ip, success=False, reason="Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.is_active:
        auth_logger.warning(f"Disabled account login attempt: {username}")
        crud.create_login_log(db, username, ip, success=False, reason="Account disabled")
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": user.username, "role": user.role, "uid": user.id})
    crud.create_login_log(db, username, ip, success=True)
    auth_logger.info(f"User logged in: {username} from {ip}")
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}
