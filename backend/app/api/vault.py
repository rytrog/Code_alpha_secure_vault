from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.schemas import VaultCreate, VaultUpdate
from ..database.models import User
from ..dependencies import get_current_user
from ..services.vault_service import create_item, get_items, get_item_decrypted, update_item, delete_item
from ..database import crud
from ..utils.response import success_response

router = APIRouter(prefix="/api/vault", tags=["Vault"])


@router.post("/")
def create_vault_item(data: VaultCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = create_item(db, current_user.id, data.title, data.category, data.data)
    return success_response(result, "Vault item created", 201)


@router.get("/")
def list_vault_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = get_items(db, current_user.id)
    return success_response(items)


@router.get("/{item_id}")
def get_vault_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = get_item_decrypted(db, item_id, current_user.id)
    return success_response(result)


@router.put("/{item_id}")
def update_vault_item(item_id: int, data: VaultUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = update_item(db, item_id, current_user.id, data.title, data.category, data.data)
    return success_response(result, "Vault item updated")


@router.delete("/{item_id}")
def delete_vault_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_item(db, item_id, current_user.id)
    return success_response(message="Vault item deleted")


# Admin routes
@router.get("/admin/all")
def admin_list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    items = crud.get_all_vault_items(db)
    return success_response([{
        "id": i.id, "user_id": i.user_id, "title": i.title,
        "category": i.category, "created_at": str(i.created_at),
    } for i in items])


@router.delete("/admin/{item_id}")
def admin_delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if not crud.admin_delete_vault_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return success_response(message="Item deleted by admin")
