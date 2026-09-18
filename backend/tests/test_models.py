"""Tests for the SQLite models and the seeding logic."""

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.db.init_db import create_tables, seed_database
from app.db.seed_data import ROOMS
from app.models import ROOM_TYPES, WEEKDAYS, Room, TimetableSlot

# Columns that would mean availability was stored instead of derived.
FORBIDDEN_COLUMNS = {
    "available",
    "availability",
    "current_status",
    "status",
    "occupied",
    "is_free",
    "is_reserved",
}


def test_room_table_has_no_stored_availability_columns(db_session):
    columns = set(inspect(Room).columns.keys())

    assert columns == {"id", "code", "name", "building", "room_type", "capacity"}
    assert columns.isdisjoint(FORBIDDEN_COLUMNS)


def test_timetable_table_has_the_expected_columns(db_session):
    columns = set(inspect(TimetableSlot).columns.keys())

    assert columns == {
        "id",
        "room_id",
        "day_of_week",
        "start_time",
        "end_time",
        "course_name",
    }


def test_timetable_slot_has_a_foreign_key_to_rooms(db_session):
    (foreign_key,) = inspect(TimetableSlot).columns["room_id"].foreign_keys

    assert foreign_key.target_fullname == "rooms.id"


def test_seed_data_is_consistent_with_the_model_constants():
    for entry in ROOMS:
        assert entry["room_type"] in ROOM_TYPES
        assert entry["capacity"] > 0
        for slot in entry["timetable"]:
            assert slot["day_of_week"] in WEEKDAYS


def test_relationship_connects_slots_to_their_room(db_session):
    room = db_session.scalar(select(Room).where(Room.code == "EN-L1"))

    assert len(room.timetable) == 4
    assert {slot.room.code for slot in room.timetable} == {"EN-L1"}
    assert {slot.room_id for slot in room.timetable} == {room.id}


def test_seeding_is_idempotent(db_session):
    # The fixture already seeded once.
    assert seed_database(db_session) == 0
    assert len(db_session.scalars(select(Room)).all()) == len(ROOMS)


def test_seeding_is_deterministic(tmp_path):
    def seed_into(name: str) -> list[tuple]:
        engine = create_engine(f"sqlite:///{(tmp_path / name).as_posix()}")
        create_tables(engine)
        with sessionmaker(bind=engine)() as db:
            seed_database(db)
            snapshot = [
                (
                    room.code,
                    room.name,
                    room.building,
                    room.room_type,
                    room.capacity,
                    tuple(
                        (
                            slot.day_of_week,
                            slot.start_time.isoformat(),
                            slot.end_time.isoformat(),
                            slot.course_name,
                        )
                        for slot in room.timetable
                    ),
                )
                for room in db.scalars(select(Room).order_by(Room.id)).all()
            ]
        Base.metadata.drop_all(engine)
        engine.dispose()
        return snapshot

    assert seed_into("first.db") == seed_into("second.db")