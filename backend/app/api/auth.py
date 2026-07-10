from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.schemas import UserRegister, UserLogin, TokenResponse
from ..services.auth_service import register_user, login_user
from ..utils.helpers import extract_ip
from ..utils.response import success_response

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register")
def register(data: UserRegister, request: Request, db: Session = Depends(get_db)):
    ip = extract_ip(request)
    result = register_user(db, data.username, data.email, data.password, ip)
    return success_response(result, "Registration successful", 201)


@router.post("/login", response_model=None)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip = extract_ip(request)
    result = login_user(db, data.username, data.password, ip)
    return result


@router.post("/logout")
def logout():
    return success_response(message="Logged out successfully")
