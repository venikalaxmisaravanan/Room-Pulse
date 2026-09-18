"""Create and seed the local SQLite database.

Usage, from the `backend` folder:

    python -m app.db.init_db            # create tables, seed if empty
    python -m app.db.init_db --reset    # delete everything and seed again

The FastAPI app also calls `init_database()` on startup, so a fresh checkout
works without running this file by hand. Seeding only happens when the room
table is empty, which keeps the data deterministic.
"""

import argparse
from datetime import time

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import DATABASE_PATH
from app.core.database import Base, engine
from app.db.seed_data import ROOMS
from app.models import Room, TimetableSlot  # noqa: F401  (registers the tables)


def create_tables(target_engine: Engine | None = None) -> None:
    """Create any table that does not exist yet."""
    Base.metadata.create_all(target_engine or engine)


def seed_database(db: Session) -> int:
    """Insert the prototype rooms and their timetable slots.

    Returns how many rooms were inserted, or 0 when the catalogue already has
    data (so calling this twice cannot duplicate anything).
    """
    if db.scalar(select(Room).limit(1)) is not None:
        return 0

    for entry in ROOMS:
        room = Room(
            code=entry["code"],
            name=entry["name"],
            building=entry["building"],
            room_type=entry["room_type"],
            capacity=entry["capacity"],
        )
        for slot in entry["timetable"]:
            room.timetable.append(
                TimetableSlot(
                    day_of_week=slot["day_of_week"],
                    start_time=time.fromisoformat(slot["start_time"]),
                    end_time=time.fromisoformat(slot["end_time"]),
                    course_name=slot["course_name"],
                )
            )
        db.add(room)

    db.commit()
    return len(ROOMS)


def init_database(target_engine: Engine | None = None, reset: bool = False) -> int:
    """Create the tables and seed them when needed. Returns rooms inserted."""
    engine_to_use = target_engine or engine

    if reset:
        Base.metadata.drop_all(engine_to_use)

    create_tables(engine_to_use)

    with Session(engine_to_use) as db:
        return seed_database(db)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create and seed the RoomPulse SQLite database."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete existing data and seed from scratch",
    )
    args = parser.parse_args()

    inserted = init_database(reset=args.reset)

    if inserted:
        print(f"Seeded {inserted} rooms into {DATABASE_PATH}")
    else:
        print(
            f"Room catalogue already present in {DATABASE_PATH} "
            "— nothing to do (use --reset to rebuild it)."
        )


if __name__ == "__main__":
    main()
