from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    vault_items = relationship("VaultItem", back_populates="owner", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class VaultItem(Base):
    __tablename__ = "vault_items"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, default="note")
    encrypted_data = Column(Text, nullable=False)
    iv = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    owner = relationship("User", back_populates="vault_items")


class AttackLog(Base):
    __tablename__ = "attack_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=_utcnow, index=True)
    ip_address = Column(String(50), nullable=False, index=True)
    username = Column(String(50), nullable=True)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), default="GET")
    payload = Column(Text, nullable=True)
    threat_score = Column(Integer, default=0)
    attack_type = Column(String(50), nullable=True)
    severity = Column(String(20), default="safe", index=True)
    action = Column(String(20), default="allowed")
    reason = Column(Text, nullable=True)
    status_code = Column(Integer, default=200)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(20), nullable=True)


class LoginLog(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=_utcnow)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(50), nullable=False)
    success = Column(Boolean, default=False)
    reason = Column(String(200), nullable=True)


class AIReport(Base):
    __tablename__ = "ai_reports"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_type = Column(String(20), default="daily")
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=_utcnow)
    generated_by = Column(String(50), default="system")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="chat_messages")


class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip_address = Column(String(50), unique=True, nullable=False)
    reason = Column(Text, nullable=True)
    blocked_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=True)
