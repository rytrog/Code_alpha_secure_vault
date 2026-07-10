import os
import sys
from .database.database import init_db, init_from_schema, SessionLocal
from .database.seed import seed_all
from .utils.logger import system_logger
from .config import settings


def on_startup():
    """Application startup handler - initializes all components."""
    system_logger.info("=" * 60)
    system_logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    system_logger.info(f"  AI-Powered Cloud Secure Data Vault")
    system_logger.info(f"  SQL Injection Defense Platform")
    system_logger.info("=" * 60)

    # ── 1. Ensure directories exist ──────────────────────
    directories = [settings.LOG_DIR, settings.EXPORT_DIR, os.path.dirname(settings.DB_PATH)]
    for d in directories:
        os.makedirs(d, exist_ok=True)
    system_logger.info("[STARTUP] Directories verified")

    # ── 2. Initialize database ───────────────────────────
    try:
        init_db()
        system_logger.info("[STARTUP] Database tables created via SQLAlchemy ORM")
    except Exception as e:
        system_logger.error(f"[STARTUP] ORM table creation failed: {e}")
        try:
            init_from_schema()
            system_logger.info("[STARTUP] Database initialized from schema.sql (fallback)")
        except Exception as e2:
            system_logger.critical(f"[STARTUP] Database initialization failed completely: {e2}")
            sys.exit(1)

    # ── 3. Seed initial data ─────────────────────────────
    try:
        db = SessionLocal()
        seed_all(db)
        db.close()
        system_logger.info("[STARTUP] Seed data initialized")
    except Exception as e:
        system_logger.error(f"[STARTUP] Seeding failed (non-fatal): {e}")

    # ── 4. Validate configuration ────────────────────────
    warnings = []
    if settings.JWT_SECRET_KEY == "sentinelx-super-secret-key-change-in-production-2026":
        warnings.append("JWT_SECRET_KEY is using default value - change in production")
    if settings.AES_ENCRYPTION_KEY == "0" * 64:
        warnings.append("AES_ENCRYPTION_KEY is using default value - change in production")
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
        warnings.append("GROQ_API_KEY not configured - AI features will use fallback responses")
    if settings.DEBUG:
        warnings.append("DEBUG mode is enabled - disable in production")

    for w in warnings:
        system_logger.warning(f"[CONFIG] {w}")

    # ── 5. Log startup summary ───────────────────────────
    system_logger.info(f"[STARTUP] Database: {settings.DB_PATH}")
    system_logger.info(f"[STARTUP] Logs: {settings.LOG_DIR}")
    system_logger.info(f"[STARTUP] Rate limit: {settings.RATE_LIMIT_PER_MINUTE} req/min")
    system_logger.info(f"[STARTUP] CORS origins: {settings.CORS_ORIGINS}")
    system_logger.info(f"[STARTUP] AI enabled: {bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here')}")
    system_logger.info("=" * 60)
    system_logger.info(f"  {settings.APP_NAME} started successfully")
    system_logger.info(f"  Swagger UI: http://localhost:8000/docs")
    system_logger.info("=" * 60)
