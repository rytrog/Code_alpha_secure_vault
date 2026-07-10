from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..database import crud
from ..security.encryption import encrypt_data, decrypt_data
from ..security.validators import validate_vault_category


def create_item(db: Session, user_id: int, title: str, category: str, data: str) -> dict:
    if not validate_vault_category(category):
        raise HTTPException(status_code=400, detail=f"Invalid category. Use: note, password, api_key, document, banking, credential, image")
    encrypted, iv = encrypt_data(data)
    item = crud.create_vault_item(db, user_id, title, category, encrypted, iv)
    return {"id": item.id, "title": item.title, "category": item.category, "created_at": str(item.created_at)}


def get_items(db: Session, user_id: int) -> list[dict]:
    items = crud.get_vault_items(db, user_id)
    return [{
        "id": i.id, "title": i.title, "category": i.category,
        "created_at": str(i.created_at), "updated_at": str(i.updated_at)
    } for i in items]


def get_item_decrypted(db: Session, item_id: int, user_id: int) -> dict:
    item = crud.get_vault_item(db, item_id, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="Vault item not found")
    decrypted = decrypt_data(item.encrypted_data, item.iv)
    return {
        "id": item.id, "title": item.title, "category": item.category,
        "decrypted_data": decrypted, "created_at": str(item.created_at)
    }


def update_item(db: Session, item_id: int, user_id: int, title=None, category=None, data=None) -> dict:
    kwargs = {}
    if title:
        kwargs["title"] = title
    if category:
        if not validate_vault_category(category):
            raise HTTPException(status_code=400, detail="Invalid category")
        kwargs["category"] = category
    if data:
        enc, iv = encrypt_data(data)
        kwargs["encrypted_data"] = enc
        kwargs["iv"] = iv
    item = crud.update_vault_item(db, item_id, user_id, **kwargs)
    if not item:
        raise HTTPException(status_code=404, detail="Vault item not found")
    return {"id": item.id, "title": item.title, "category": item.category}


def delete_item(db: Session, item_id: int, user_id: int) -> bool:
    if not crud.delete_vault_item(db, item_id, user_id):
        raise HTTPException(status_code=404, detail="Vault item not found")
    return True
