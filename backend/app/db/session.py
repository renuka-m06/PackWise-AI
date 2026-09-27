from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

# Configure SQLAlchemy engine with connection pool
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding database sessions.
    Automatically closes session upon request completion and rolls back on exception.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session rollback triggered by exception: {e}")
        raise
    finally:
        db.close()


def get_db_optional() -> Generator[Session | None, None, None]:
    """
    FastAPI dependency yielding database session if database is accessible,
    or None if offline or in testing fallback mode.
    """
    db = None
    try:
        db = SessionLocal()
    except Exception as e:
        logger.debug(f"Optional DB session initialization failed: {e}")
        yield None
        return

    try:
        yield db
    except Exception:
        if db is not None:
            db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

