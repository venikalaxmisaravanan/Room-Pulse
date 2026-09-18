"""SQLite database setup.

One file, one engine, one session factory. There are no migrations in this
prototype: the tables are created from the models in `app/models/` on startup
or by running `python -m app.db.init_db`.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL

# check_same_thread=False is needed because FastAPI can handle a request on a
# different thread than the one that opened the connection.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class that every RoomPulse table inherits from."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency that gives each request its own database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
