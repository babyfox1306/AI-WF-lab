from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create all database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yield a database session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
