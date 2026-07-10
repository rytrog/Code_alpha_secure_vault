from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import User
from ..database import crud
from ..dependencies import require_admin
from ..services.attack_service import get_attack_logs, get_attack_by_id, search_logs, get_analytics
from ..utils.response import success_response

router = APIRouter(prefix="/api/attacks", tags=["Attacks"])


@router.get("/")
def list_attacks(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    logs = get_attack_logs(db, limit, offset)
    return success_response(logs)


@router.get("/search")
def search_attacks(
    attack_type: str = None, ip: str = None, endpoint: str = None,
    severity: str = None, username: str = None,
    date_from: str = None, date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    filters = {k: v for k, v in {
        "attack_type": attack_type, "ip": ip, "endpoint": endpoint,
        "severity": severity, "username": username,
        "date_from": date_from, "date_to": date_to,
    }.items() if v}
    results = search_logs(db, filters)
    return success_response(results)


@router.get("/analytics")
def attack_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    data = get_analytics(db)
    return success_response(data)


@router.get("/{log_id}")
def get_attack(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    log = get_attack_by_id(db, log_id)
    if not log:
        return success_response(None, "Attack log not found", 404)
    return success_response(log)


@router.delete("/old")
def delete_old(days: int = Query(30), db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    count = crud.delete_old_attack_logs(db, days)
    return success_response({"deleted": count}, f"Deleted {count} old logs")
