from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import User
from ..dependencies import require_admin
from ..services.dashboard_service import get_dashboard_stats, get_chart_data, get_recent_activity
from ..services.analytics_service import get_full_analytics
from ..utils.response import success_response

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    stats = get_dashboard_stats(db)
    return success_response(stats)


@router.get("/charts")
def dashboard_charts(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    data = get_chart_data(db)
    return success_response(data)


@router.get("/recent")
def recent_activity(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    data = get_recent_activity(db)
    return success_response(data)


@router.get("/analytics")
def full_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    data = get_full_analytics(db)
    return success_response(data)
