"""Evaluate the whole catalogue with the availability engine.

This keeps the FastAPI route thin: the route loads rooms and asks "what time
is it?", this module turns each room's timetable into an AVAILABLE/IN_CLASS
answer. Capacity is passed through untouched — Stage 3 has no occupancy
data, so FULL cannot be decided yet.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Room
from app.schemas.availability import (
    ActiveClassRead,
    AvailabilityListResponse,
    RoomAvailabilityRead,
)
from app.services.availability import AVAILABLE, IN_CLASS, decide
from app.services.room_service import _slot_sort_key


def _format_time(value) -> str:
    """Return "HH:MM" for a time object or an ISO time string."""
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    return str(value)[:5]


def evaluate_catalogue(db: Session, now: datetime) -> AvailabilityListResponse:
    """Load every room, decide its state at ``now``, return the API payload."""
    rooms = db.scalars(select(Room).order_by(Room.code)).all()

    results: list[RoomAvailabilityRead] = []
    for room in rooms:
        ordered_slots = sorted(room.timetable, key=_slot_sort_key)
        decision = decide(ordered_slots, now)

        active_class = None
        if decision.active_slot is not None:
            active_class = ActiveClassRead(
                day_of_week=decision.active_slot.day_of_week,
                start_time=_format_time(decision.active_slot.start_time),
                end_time=_format_time(decision.active_slot.end_time),
                course_name=decision.active_slot.course_name,
            )

        results.append(
            RoomAvailabilityRead(
                id=room.id,
                code=room.code,
                name=room.name,
                building=room.building,
                room_type=room.room_type,
                capacity=room.capacity,
                state=decision.state,
                reason=decision.reason,
                active_class=active_class,
                timetable=[
                    {
                        "id": slot.id,
                        "day_of_week": slot.day_of_week,
                        "start_time": _format_time(slot.start_time),
                        "end_time": _format_time(slot.end_time),
                        "course_name": slot.course_name,
                    }
                    for slot in ordered_slots
                ],
            )
        )

    available_count = sum(1 for item in results if item.state == AVAILABLE)
    in_class_count = sum(1 for item in results if item.state == IN_CLASS)

    return AvailabilityListResponse(
        evaluated_at=now,
        count=len(results),
        available_count=available_count,
        in_class_count=in_class_count,
        rooms=results,
    )


__all__ = ["evaluate_catalogue"]
