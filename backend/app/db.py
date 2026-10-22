"""Motor de SQLAlchemy y sesión por solicitud."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

engine = create_engine(get_settings().url_sqlalchemy, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Una sesión por solicitud. Los endpoints de escritura hacen commit explícito;
    lo que no se confirmó se descarta al cerrar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
