from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from ..config import settings

DATABASE_PATH = settings.DB_PATH
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Direct session for middleware/services."""
    return SessionLocal()


def init_db():
    """Create all tables."""
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)


def init_from_schema():
    """Run raw schema.sql."""
    import sqlite3
    conn = sqlite3.connect(DATABASE_PATH)
    schema_path = settings.SCHEMA_PATH
    try:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()
