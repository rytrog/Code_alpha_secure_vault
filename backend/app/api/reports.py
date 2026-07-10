from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import User
from ..dependencies import require_admin
from ..services.report_service import get_reports, get_report_by_id
from ..utils.response import success_response

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/")
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    reports = get_reports(db)
    return success_response(reports)


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    report = get_report_by_id(db, report_id)
    if not report:
        return success_response(None, "Report not found", 404)
    return success_response(report)
