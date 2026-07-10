from sqlalchemy.orm import Session
from ..database import crud


def get_full_analytics(db: Session) -> dict:
    attacks = crud.count_attacks_today(db)
    logins = crud.count_logins_today(db)
    return {
        "today": {"attacks": attacks, "logins": logins},
        "weekly": {
            "attack_types": crud.get_attack_type_distribution(db, 7),
            "severity": crud.get_severity_distribution(db, 7),
            "daily_attacks": crud.get_daily_attack_counts(db, 7),
            "daily_logins": crud.get_daily_login_counts(db, 7),
        },
        "monthly": {
            "attack_types": crud.get_attack_type_distribution(db, 30),
            "daily_attacks": crud.get_daily_attack_counts(db, 30),
        },
        "top_ips": crud.get_top_attacker_ips(db, 10),
        "top_endpoints": crud.get_top_attacked_endpoints(db, 10),
    }
