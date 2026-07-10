from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone, timedelta
from .models import User, VaultItem, AttackLog, LoginLog, AIReport, ChatMessage, BlockedIP


# ── Users ────────────────────────────────────────
def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, username: str, email: str, hashed_password: str, role: str = "user") -> User:
    user = User(username=username, email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def toggle_user_active(db: Session, user_id: int) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
    return user

def count_users(db: Session) -> int:
    return db.query(func.count(User.id)).scalar() or 0


# ── Vault ────────────────────────────────────────
def create_vault_item(db: Session, user_id: int, title: str, category: str, encrypted_data: str, iv: str) -> VaultItem:
    item = VaultItem(user_id=user_id, title=title, category=category, encrypted_data=encrypted_data, iv=iv)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_vault_items(db: Session, user_id: int) -> list[VaultItem]:
    return db.query(VaultItem).filter(VaultItem.user_id == user_id).order_by(desc(VaultItem.created_at)).all()

def get_vault_item(db: Session, item_id: int, user_id: int) -> VaultItem | None:
    return db.query(VaultItem).filter(VaultItem.id == item_id, VaultItem.user_id == user_id).first()

def update_vault_item(db: Session, item_id: int, user_id: int, **kwargs) -> VaultItem | None:
    item = get_vault_item(db, item_id, user_id)
    if item:
        for k, v in kwargs.items():
            if v is not None:
                setattr(item, k, v)
        item.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(item)
    return item

def delete_vault_item(db: Session, item_id: int, user_id: int) -> bool:
    item = get_vault_item(db, item_id, user_id)
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def count_vault_items(db: Session, user_id: int | None = None) -> int:
    q = db.query(func.count(VaultItem.id))
    if user_id:
        q = q.filter(VaultItem.user_id == user_id)
    return q.scalar() or 0

def get_all_vault_items(db: Session) -> list[VaultItem]:
    return db.query(VaultItem).order_by(desc(VaultItem.created_at)).all()

def admin_delete_vault_item(db: Session, item_id: int) -> bool:
    item = db.query(VaultItem).filter(VaultItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False


# ── Attack Logs ──────────────────────────────────
def create_attack_log(db: Session, data: dict) -> AttackLog:
    log = AttackLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_attack_logs(db: Session, limit: int = 100, offset: int = 0) -> list[AttackLog]:
    return db.query(AttackLog).order_by(desc(AttackLog.timestamp)).offset(offset).limit(limit).all()

def get_attack_log_by_id(db: Session, log_id: int) -> AttackLog | None:
    return db.query(AttackLog).filter(AttackLog.id == log_id).first()

def search_attack_logs(db: Session, filters: dict) -> list[AttackLog]:
    q = db.query(AttackLog)
    if filters.get("attack_type"):
        q = q.filter(AttackLog.attack_type == filters["attack_type"])
    if filters.get("ip"):
        q = q.filter(AttackLog.ip_address.contains(filters["ip"]))
    if filters.get("endpoint"):
        q = q.filter(AttackLog.endpoint.contains(filters["endpoint"]))
    if filters.get("severity"):
        q = q.filter(AttackLog.severity == filters["severity"])
    if filters.get("username"):
        q = q.filter(AttackLog.username.contains(filters["username"]))
    if filters.get("date_from"):
        q = q.filter(AttackLog.timestamp >= filters["date_from"])
    if filters.get("date_to"):
        q = q.filter(AttackLog.timestamp <= filters["date_to"])
    return q.order_by(desc(AttackLog.timestamp)).limit(200).all()

def count_attacks_today(db: Session) -> dict:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total = db.query(func.count(AttackLog.id)).filter(AttackLog.timestamp >= today).scalar() or 0
    blocked = db.query(func.count(AttackLog.id)).filter(AttackLog.timestamp >= today, AttackLog.action == "blocked").scalar() or 0
    return {"total": total, "blocked": blocked, "allowed": total - blocked}

def get_attack_type_distribution(db: Session, days: int = 7) -> list:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(AttackLog.attack_type, func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since, AttackLog.attack_type.isnot(None)
    ).group_by(AttackLog.attack_type).all()
    return [{"type": r[0], "count": r[1]} for r in rows]

def get_severity_distribution(db: Session, days: int = 7) -> list:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(AttackLog.severity, func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).group_by(AttackLog.severity).all()
    return [{"severity": r[0], "count": r[1]} for r in rows]

def get_daily_attack_counts(db: Session, days: int = 7) -> list:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(func.date(AttackLog.timestamp), func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).group_by(func.date(AttackLog.timestamp)).all()
    return [{"date": str(r[0]), "count": r[1]} for r in rows]

def get_top_attacker_ips(db: Session, limit: int = 5) -> list:
    rows = db.query(AttackLog.ip_address, func.count(AttackLog.id)).filter(
        AttackLog.action == "blocked"
    ).group_by(AttackLog.ip_address).order_by(desc(func.count(AttackLog.id))).limit(limit).all()
    return [{"ip": r[0], "count": r[1]} for r in rows]

def get_top_attacked_endpoints(db: Session, limit: int = 5) -> list:
    rows = db.query(AttackLog.endpoint, func.count(AttackLog.id)).filter(
        AttackLog.action == "blocked"
    ).group_by(AttackLog.endpoint).order_by(desc(func.count(AttackLog.id))).limit(limit).all()
    return [{"endpoint": r[0], "count": r[1]} for r in rows]

def delete_old_attack_logs(db: Session, days: int = 30) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    count = db.query(AttackLog).filter(AttackLog.timestamp < cutoff).delete()
    db.commit()
    return count


# ── Login Logs ───────────────────────────────────
def create_login_log(db: Session, username: str, ip_address: str, success: bool, reason: str = None) -> LoginLog:
    log = LoginLog(username=username, ip_address=ip_address, success=success, reason=reason)
    db.add(log)
    db.commit()
    return log

def get_login_logs(db: Session, limit: int = 50) -> list[LoginLog]:
    return db.query(LoginLog).order_by(desc(LoginLog.timestamp)).limit(limit).all()

def count_logins_today(db: Session) -> dict:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    success = db.query(func.count(LoginLog.id)).filter(LoginLog.timestamp >= today, LoginLog.success == True).scalar() or 0
    failed = db.query(func.count(LoginLog.id)).filter(LoginLog.timestamp >= today, LoginLog.success == False).scalar() or 0
    return {"successful": success, "failed": failed}

def get_daily_login_counts(db: Session, days: int = 7) -> list:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(func.date(LoginLog.timestamp), LoginLog.success, func.count(LoginLog.id)).filter(
        LoginLog.timestamp >= since
    ).group_by(func.date(LoginLog.timestamp), LoginLog.success).all()
    return [{"date": str(r[0]), "success": r[1], "count": r[2]} for r in rows]


# ── AI Reports ───────────────────────────────────
def create_ai_report(db: Session, report_type: str, content: str, generated_by: str = "system") -> AIReport:
    report = AIReport(report_type=report_type, content=content, generated_by=generated_by)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_ai_reports(db: Session, limit: int = 20) -> list[AIReport]:
    return db.query(AIReport).order_by(desc(AIReport.generated_at)).limit(limit).all()

def get_ai_report_by_id(db: Session, report_id: int) -> AIReport | None:
    return db.query(AIReport).filter(AIReport.id == report_id).first()


# ── Chat ─────────────────────────────────────────
def save_chat_message(db: Session, user_id: int, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(user_id=user_id, role=role, content=content)
    db.add(msg)
    db.commit()
    return msg

def get_chat_history(db: Session, user_id: int, limit: int = 20) -> list[ChatMessage]:
    return db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(desc(ChatMessage.timestamp)).limit(limit).all()

def clear_chat_history(db: Session, user_id: int):
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
