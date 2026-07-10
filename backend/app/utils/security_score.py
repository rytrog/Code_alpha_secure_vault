from sqlalchemy.orm import Session
from ..database import crud


def compute_security_score(db: Session) -> int:
    """
    Compute overall security score (0-100).
    Higher = more secure.
    """
    score = 100

    attacks = crud.count_attacks_today(db)
    logins = crud.count_logins_today(db)

    # Deduct for blocked attacks
    if attacks["blocked"] > 0:
        score -= min(30, attacks["blocked"] * 3)

    # Deduct for failed logins
    if logins["failed"] > 0:
        score -= min(20, logins["failed"] * 4)

    # Deduct for high volume of total requests
    if attacks["total"] > 50:
        score -= 10
    if attacks["total"] > 100:
        score -= 10

    return max(0, min(100, score))


def get_threat_level(score: int) -> str:
    if score >= 80:
        return "Low"
    elif score >= 60:
        return "Medium"
    elif score >= 40:
        return "High"
    else:
        return "Critical"
