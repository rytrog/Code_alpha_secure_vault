from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import crud
from ..dependencies import get_current_user, require_admin
from ..database.models import User
from ..security.password import hash_password
from ..utils.response import success_response

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return success_response({
        "id": current_user.id, "username": current_user.username,
        "email": current_user.email, "role": current_user.role,
        "is_active": current_user.is_active, "created_at": str(current_user.created_at),
    })


@router.get("/")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    users = crud.get_all_users(db)
    return success_response([{
        "id": u.id, "username": u.username, "email": u.email,
        "role": u.role, "is_active": u.is_active, "created_at": str(u.created_at)
    } for u in users])


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(message="User deleted")


@router.patch("/{user_id}/toggle")
def toggle_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = crud.toggle_user_active(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response({"is_active": user.is_active}, "User status updated")


@router.patch("/{user_id}/reset-password")
def reset_password(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password("Reset@2026!")
    db.commit()
    return success_response(message="Password reset to default")


@router.patch("/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: str = Query(..., description="The role to assign: 'admin' or 'user'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    if new_role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'user'")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = new_role
    db.commit()
    return success_response({"role": user.role}, f"User role updated to {new_role}")
