from sqlalchemy.orm import Session
from .models import User, AttackLog, LoginLog, VaultItem
from ..security.password import hash_password
from ..security.encryption import encrypt_data
from ..config import settings
from datetime import datetime, timezone, timedelta
import random


def seed_admin(db: Session):
    """Create default admin user if not exists."""
    from . import crud
    existing = crud.get_user_by_username(db, settings.ADMIN_USERNAME)
    if not existing:
        crud.create_user(
            db,
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role="admin"
        )
        print("[SEED] Admin user created")


def seed_demo_user(db: Session):
    """Create a demo standard user."""
    from . import crud
    existing = crud.get_user_by_username(db, "demo_user")
    if not existing:
        crud.create_user(
            db,
            username="demo_user",
            email="demo@sentinelx.io",
            hashed_password=hash_password("Demo@2026!"),
            role="user"
        )
        print("[SEED] Demo user created")


def seed_attack_logs(db: Session, count: int = 25):
    """Generate sample attack logs for demo."""
    from . import crud
    existing = db.query(AttackLog).count()
    if existing >= count:
        return

    sample_attacks = [
        {"payload": "' OR '1'='1' --", "attack_type": "boolean_injection", "threat_score": 75, "severity": "high"},
        {"payload": "UNION SELECT * FROM users", "attack_type": "union_injection", "threat_score": 85, "severity": "critical"},
        {"payload": "'; DROP TABLE users; --", "attack_type": "keyword_injection", "threat_score": 95, "severity": "critical"},
        {"payload": "1; WAITFOR DELAY '0:0:5'", "attack_type": "time_based_injection", "threat_score": 65, "severity": "high"},
        {"payload": "admin'--", "attack_type": "comment_injection", "threat_score": 45, "severity": "medium"},
        {"payload": "%27%20OR%201%3D1", "attack_type": "encoded_payload", "threat_score": 70, "severity": "high"},
        {"payload": "1 AND 1=1", "attack_type": "boolean_injection", "threat_score": 35, "severity": "medium"},
        {"payload": "xp_cmdshell('dir')", "attack_type": "system_function_injection", "threat_score": 90, "severity": "critical"},
        {"payload": "SLEEP(5)", "attack_type": "time_based_injection", "threat_score": 60, "severity": "medium"},
        {"payload": "INFORMATION_SCHEMA.TABLES", "attack_type": "system_function_injection", "threat_score": 55, "severity": "medium"},
    ]

    endpoints = ["/api/auth/login", "/api/vault", "/api/users", "/api/dashboard", "/api/attacks"]
    ips = ["192.168.1.100", "10.0.0.55", "172.16.0.200", "203.0.113.42", "198.51.100.7", "45.33.32.156"]

    for i in range(count):
        attack = random.choice(sample_attacks)
        hours_ago = random.randint(0, 168)
        crud.create_attack_log(db, {
            "ip_address": random.choice(ips),
            "username": random.choice(["admin", "demo_user", None, "unknown"]),
            "endpoint": random.choice(endpoints),
            "method": random.choice(["GET", "POST", "PUT"]),
            "payload": attack["payload"],
            "threat_score": attack["threat_score"],
            "attack_type": attack["attack_type"],
            "severity": attack["severity"],
            "action": "blocked" if attack["threat_score"] > 30 else "allowed",
            "reason": f"SQL Injection detected: {attack['attack_type']}",
            "status_code": 403 if attack["threat_score"] > 30 else 200,
            "user_agent": "Mozilla/5.0 (SentinelX Demo)",
            "request_id": f"demo-{i:04d}",
        })
    print(f"[SEED] {count} attack logs created")


def seed_login_logs(db: Session, count: int = 15):
    """Generate sample login logs."""
    existing = db.query(LoginLog).count()
    if existing >= count:
        return

    for i in range(count):
        success = random.choice([True, True, True, False])
        db.add(LoginLog(
            username=random.choice(["admin", "demo_user", "unknown_user"]),
            ip_address=random.choice(["192.168.1.1", "10.0.0.1", "172.16.0.1"]),
            success=success,
            reason=None if success else "Invalid credentials",
        ))
    db.commit()
    print(f"[SEED] {count} login logs created")


def seed_vault_items(db: Session):
    """Create sample encrypted vault items for demo user."""
    from . import crud
    demo = crud.get_user_by_username(db, "demo_user")
    if not demo:
        return
    existing = crud.count_vault_items(db, demo.id)
    if existing > 0:
        return

    items = [
        ("AWS Access Key", "api_key", "AKIAIOSFODNN7EXAMPLE"),
        ("Database Password", "password", "Str0ngP@ss!2026"),
        ("Server SSH Key", "credential", "ssh-rsa AAAAB3Nza...example"),
        ("Project Notes", "note", "Deploy to production after security audit"),
        ("Bank Account", "banking", "Account: 1234567890 | Routing: 021000021"),
    ]

    for title, category, data in items:
        enc_data, iv = encrypt_data(data)
        crud.create_vault_item(db, demo.id, title, category, enc_data, iv)
    print("[SEED] Vault items created for demo_user")


def seed_all(db: Session):
    """Run all seed functions."""
    seed_admin(db)
    seed_demo_user(db)
    seed_attack_logs(db)
    seed_login_logs(db)
    seed_vault_items(db)
    print("[SEED] All seed data initialized")
