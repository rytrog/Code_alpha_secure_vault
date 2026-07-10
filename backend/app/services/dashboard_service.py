from sqlalchemy.orm import Session
from ..database import crud
from ..utils.security_score import compute_security_score, get_threat_level


def get_dashboard_stats(db: Session) -> dict:
    attacks = crud.count_attacks_today(db)
    logins = crud.count_logins_today(db)
    score = compute_security_score(db)

    return {
        "total_users": crud.count_users(db),
        "encrypted_records": crud.count_vault_items(db),
        "today_requests": attacks["total"],
        "blocked_requests": attacks["blocked"],
        "successful_logins": logins["successful"],
        "failed_logins": logins["failed"],
        "threat_level": get_threat_level(score),
        "security_score": score,
    }


def get_chart_data(db: Session) -> dict:
    return {
        "attack_types": crud.get_attack_type_distribution(db),
        "daily_attacks": crud.get_daily_attack_counts(db),
        "login_activity": crud.get_daily_login_counts(db),
        "severity_distribution": crud.get_severity_distribution(db),
        "top_ips": crud.get_top_attacker_ips(db),
        "top_endpoints": crud.get_top_attacked_endpoints(db),
    }


def get_recent_activity(db: Session) -> dict:
    return {
        "recent_attacks": [_attack_dict(a) for a in crud.get_attack_logs(db, limit=10)],
        "recent_logins": [_login_dict(l) for l in crud.get_login_logs(db, limit=10)],
    }


def _attack_dict(a) -> dict:
    return {
        "id": a.id, "timestamp": str(a.timestamp), "ip_address": a.ip_address,
        "endpoint": a.endpoint, "threat_score": a.threat_score,
        "severity": a.severity, "action": a.action, "attack_type": a.attack_type,
    }


def _login_dict(l) -> dict:
    return {
        "id": l.id, "timestamp": str(l.timestamp), "username": l.username,
        "ip_address": l.ip_address, "success": l.success, "reason": l.reason,
    }
