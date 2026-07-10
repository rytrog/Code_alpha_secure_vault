import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "SentinelX")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///../../database/sentinelx.db")
    DB_PATH: str = str(BASE_DIR.parent / "database" / "sentinelx.db")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    AES_ENCRYPTION_KEY: str = os.getenv("AES_ENCRYPTION_KEY", "0" * 64)

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5500").split(",")

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@sentinelx.io")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Admin@SentinelX2026")

    SCHEMA_PATH: str = str(BASE_DIR.parent / "database" / "schema.sql")
    LOG_DIR: str = str(BASE_DIR / "app" / "logs")
    EXPORT_DIR: str = str(BASE_DIR / "app" / "exports" / "reports")

settings = Settings()
