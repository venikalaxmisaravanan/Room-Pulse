"""Evaluate the whole catalogue with the availability engine.

This keeps the FastAPI route thin: the route loads rooms and asks "what time
is it?", this module turns each room's timetable plus its simulated
occupancy reading into a FULL / IN_CLASS / OCCUPIED / AVAILABLE answer.

Occupancy is transient sensor input, not catalogue data: the readings are
built in memory by ``app.services.occupancy`` and never stored in SQLite.
The Room table still has no availability, occupancy or status columns.
"""

from __future__ import annotations

from datetime import datetime
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import SENSOR_FRESHNESS_SECONDS
from app.models import Room
from app.schemas.availability import (
    ActiveClassRead,
    AvailabilityListResponse,
    OccupancyRead,
    RoomAvailabilityRead,
    SensorFreshnessRead,
)
from app.services.availability import (
    AVAILABLE,
    FULL,
    IN_CLASS,
    OCCUPIED,
    UNKNOWN,
    decide,
)
from app.services.occupancy import current_readings
from app.services.room_service import _slot_sort_key
from app.services.sensor_freshness import assess_reading

USABLE_STATE: Final[str] = AVAILABLE


def _format_time(value) -> str:
    """Return "HH:MM" for a time object or an ISO time string."""
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    return str(value)[:5]


def _reason_code(state: str, freshness) -> str:
    """Name the factual cause represented by the existing final state."""
    if state == UNKNOWN:
        if freshness.status == "STALE":
            return "SENSOR_STALE"
        return "SENSOR_MISSING"
    return state


def evaluate_catalogue(db: Session, now: datetime) -> AvailabilityListResponse:
    """Load every room, decide its state at ``now``, return the API payload.

    The same ``now`` feeds both the timetable comparison and the simulator,
    so the whole response describes one consistent moment.
    """
    rooms = db.scalars(select(Room).order_by(Room.code)).all()
    readings = {reading.code: reading for reading in current_readings(rooms, now)}

    results: list[RoomAvailabilityRead] = []
    for room in rooms:
        ordered_slots = sorted(room.timetable, key=_slot_sort_key)
        reading = readings[room.code]
        freshness = assess_reading(
            reading, now, threshold_seconds=SENSOR_FRESHNESS_SECONDS
        )
        decision = decide(
            ordered_slots,
            now,
            occupancy=reading.occupancy,
            capacity=room.capacity,
            freshness=freshness,
        )

        active_class = None
        if decision.active_slot is not None:
            active_class = ActiveClassRead(
                day_of_week=decision.active_slot.day_of_week,
                start_time=_format_time(decision.active_slot.start_time),
                end_time=_format_time(decision.active_slot.end_time),
                course_name=decision.active_slot.course_name,
            )

        occupancy_payload = OccupancyRead(
            occupancy=reading.occupancy,
            capacity=room.capacity,
            scenario=reading.scenario,
            timestamp=reading.timestamp,
            simulated=True,
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
                reason_code=_reason_code(decision.state, freshness),
                reason=decision.reason,
                active_class=active_class,
                occupancy=occupancy_payload,
                sensor_freshness=SensorFreshnessRead(
                    status=freshness.status,
                    age_seconds=freshness.age_seconds,
                    fresh=freshness.fresh,
                    sensor_note=freshness.sensor_note,
                ),
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

    counts = {
        state: 0 for state in (AVAILABLE, IN_CLASS, OCCUPIED, FULL, UNKNOWN)
    }
    for item in results:
        counts[item.state] += 1

    return AvailabilityListResponse(
        evaluated_at=now,
        count=len(results),
        available_count=counts[AVAILABLE],
        in_class_count=counts[IN_CLASS],
        occupied_count=counts[OCCUPIED],
        full_count=counts[FULL],
        rooms=results,
    )


def evaluate_catalogue_from_simulator(now: datetime) -> AvailabilityListResponse:
    """Evaluate one live tick through the same catalogue engine as REST."""
    from app.core.database import SessionLocal

    with SessionLocal() as db:
        return evaluate_catalogue(db, now)


def find_usable_rooms(
    snapshot: AvailabilityListResponse,
    building: str | None = None,
    room_type: str | None = None,
    min_capacity: int | None = None,
) -> AvailabilityListResponse:
    """Return current AVAILABLE rooms matching catalogue requirements.

    AVAILABLE is the only usable state: OCCUPIED, FULL, IN_CLASS and UNKNOWN
    each describe a current condition that prevents RoomPulse from promising
    immediate use. Existing catalogue order is retained for deterministic
    results; this function does not introduce a second ranking system.
    """
    rooms = [
        room
        for room in snapshot.rooms
        if room.state == USABLE_STATE
        and (building is None or room.building == building)
        and (room_type is None or room.room_type == room_type)
        and (min_capacity is None or room.capacity >= min_capacity)
    ]
    counts = {state: 0 for state in (AVAILABLE, IN_CLASS, OCCUPIED, FULL, UNKNOWN)}
    for room in rooms:
        counts[room.state] += 1
    return snapshot.model_copy(
        update={
            "count": len(rooms),
            "available_count": counts[AVAILABLE],
            "in_class_count": counts[IN_CLASS],
            "occupied_count": counts[OCCUPIED],
            "full_count": counts[FULL],
            "rooms": rooms,
        }
    )


__all__ = [
    "USABLE_STATE",
    "evaluate_catalogue",
    "evaluate_catalogue_from_simulator",
    "find_usable_rooms",
]
