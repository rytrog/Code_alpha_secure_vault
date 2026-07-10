from sqlalchemy.orm import Session
from ..database import crud


def get_attack_logs(db: Session, limit: int = 100, offset: int = 0) -> list:
    logs = crud.get_attack_logs(db, limit, offset)
    return [_log_to_dict(l) for l in logs]


def get_attack_by_id(db: Session, log_id: int) -> dict | None:
    log = crud.get_attack_log_by_id(db, log_id)
    return _log_to_dict(log) if log else None


def search_logs(db: Session, filters: dict) -> list:
    logs = crud.search_attack_logs(db, filters)
    return [_log_to_dict(l) for l in logs]


def get_analytics(db: Session) -> dict:
    return {
        "today": crud.count_attacks_today(db),
        "type_distribution": crud.get_attack_type_distribution(db),
        "severity_distribution": crud.get_severity_distribution(db),
        "daily_counts": crud.get_daily_attack_counts(db),
        "top_ips": crud.get_top_attacker_ips(db),
        "top_endpoints": crud.get_top_attacked_endpoints(db),
    }


def _log_to_dict(log) -> dict:
    return {
        "id": log.id, "timestamp": str(log.timestamp), "ip_address": log.ip_address,
        "username": log.username, "endpoint": log.endpoint, "method": log.method,
        "payload": log.payload, "threat_score": log.threat_score,
        "attack_type": log.attack_type, "severity": log.severity,
        "action": log.action, "reason": log.reason,
        "status_code": log.status_code, "request_id": log.request_id,
    }
