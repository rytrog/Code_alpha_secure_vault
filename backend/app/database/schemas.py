from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Auth ─────────────────────────────────────────
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    class Config:
        from_attributes = True


# ── Vault ────────────────────────────────────────
class VaultCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="note")
    data: str = Field(..., min_length=1)

class VaultUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    data: Optional[str] = None

class VaultOut(BaseModel):
    id: int
    title: str
    category: str
    decrypted_data: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    class Config:
        from_attributes = True


# ── Attack Logs ──────────────────────────────────
class AttackLogOut(BaseModel):
    id: int
    timestamp: datetime | None = None
    ip_address: str
    username: str | None = None
    endpoint: str
    method: str
    payload: str | None = None
    threat_score: int
    attack_type: str | None = None
    severity: str
    action: str
    reason: str | None = None
    status_code: int | None = None
    request_id: str | None = None
    class Config:
        from_attributes = True

class AttackLogSearch(BaseModel):
    attack_type: Optional[str] = None
    ip: Optional[str] = None
    endpoint: Optional[str] = None
    severity: Optional[str] = None
    username: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


# ── AI ───────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    reply: str
    context_used: str | None = None

class ExplainRequest(BaseModel):
    attack_log_id: int

class ReportOut(BaseModel):
    id: int
    report_type: str
    content: str
    generated_at: datetime | None = None
    class Config:
        from_attributes = True


# ── Dashboard ────────────────────────────────────
class DashboardStats(BaseModel):
    total_users: int = 0
    encrypted_records: int = 0
    today_requests: int = 0
    blocked_requests: int = 0
    successful_logins: int = 0
    failed_logins: int = 0
    threat_level: str = "Low"
    security_score: int = 100

class SystemHealth(BaseModel):
    api_status: str = "operational"
    database_status: str = "operational"
    auth_status: str = "operational"
    encryption_status: str = "operational"
    ai_status: str = "operational"
    overall: str = "healthy"
