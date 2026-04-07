from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Provide a SQLAlchemy Session for callers and ensure the session is closed after use.
    
    This generator yields a `Session` instance from `SessionLocal` for use (commonly as a dependency) and guarantees the session is closed when the caller is finished.
    
    Returns:
        sqlalchemy.orm.Session: An active database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
