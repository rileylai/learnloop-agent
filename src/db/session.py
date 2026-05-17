from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.config import get_settings

DEFAULT_DATABASE_URL = "postgresql+psycopg://learnloop:learnloop@localhost:5432/learnloop"


def get_database_url() -> str:
    settings = get_settings()
    return settings.database_url or DEFAULT_DATABASE_URL


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
