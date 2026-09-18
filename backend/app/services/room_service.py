"""Reading the room catalogue out of the database.

This module is deliberately read-only and contains no availability logic. It
loads rooms, sorts their timetable slots the way a student reads a timetable,
and converts them into the response schema.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import WEEKDAYS, Room, TimetableSlot
from app.schemas.room import RoomRead, TimetableSlotRead


def _slot_sort_key(slot: TimetableSlot) -> tuple[int, object]:
    """Sort slots Monday-first, then by start time.

    WEEKDAYS is a tuple, so `.index()` gives the Monday-first position.
    """
    return (WEEKDAYS.index(slot.day_of_week), slot.start_time)


def _to_room_read(room: Room) -> RoomRead:
    """Turn one room row into the JSON shape the dashboard uses."""
    ordered_slots = sorted(room.timetable, key=_slot_sort_key)

    return RoomRead(
        id=room.id,
        code=room.code,
        name=room.name,
        building=room.building,
        room_type=room.room_type,
        capacity=room.capacity,
        timetable=[
            TimetableSlotRead.model_validate(slot) for slot in ordered_slots
        ],
    )


def list_rooms_with_timetable(db: Session) -> list[RoomRead]:
    """Return every room in the catalogue, ordered by room code."""
    rooms = db.scalars(select(Room).order_by(Room.code)).all()
    return [_to_room_read(room) for room in rooms]
