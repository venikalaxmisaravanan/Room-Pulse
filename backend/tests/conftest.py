"""Shared pytest fixtures.

The tests never touch the real `roompulse.db`. Every test gets its own temporary
SQLite file built from the same models and the same seed data the app uses, so
the tests cannot be affected by local data.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.db.init_db import create_tables, seed_database
from app.main import app


@pytest.fixture()
def session_factory(tmp_path):
    """A session factory pointing at a fresh, seeded temporary database."""
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    create_tables(engine)

    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as db:
        seed_database(db)

    yield factory

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(session_factory) -> Session:
    """One database session for tests that read the models directly."""
    with session_factory() as db:
        yield db


@pytest.fixture()
def client(session_factory):
    """A TestClient that uses the temporary database instead of the real one.

    The client is not used as a context manager on purpose: that would run the
    app's lifespan and create the real `roompulse.db` while testing.
    """
    def override_get_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()