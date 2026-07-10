from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database.database import get_db
from ..utils.response import success_response
from ..utils.security_score import compute_security_score, get_threat_level
from ..config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("/")
def health_check():
    return success_response({
        "status": "operational",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }, "System is healthy")


@router.get("/detailed")
def detailed_health(db: Session = Depends(get_db)):
    # Check database connectivity
    db_status = "operational"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # Check AI configuration
    ai_status = "operational"
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
        ai_status = "not configured"

    # Check encryption key
    enc_status = "operational"
    if not settings.AES_ENCRYPTION_KEY or len(settings.AES_ENCRYPTION_KEY) != 64:
        enc_status = "misconfigured"

    score = compute_security_score(db)

    return success_response({
        "api_status": "operational",
        "database_status": db_status,
        "auth_status": "operational",
        "encryption_status": enc_status,
        "ai_status": ai_status,
        "security_score": score,
        "threat_level": get_threat_level(score),
        "overall": "healthy" if db_status == "operational" else "degraded",
    })
