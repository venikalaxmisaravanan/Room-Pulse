"""Response schemas for the availability endpoint.

These describe derived data: nothing here is stored in SQLite. Each room's
state is computed from its timetable and the evaluated moment, then returned
with a human-readable reason so the dashboard can explain itself.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActiveClassRead(BaseModel):
    """The timetable slot that is currently in session, if any."""

    model_config = ConfigDict(from_attributes=True)

    day_of_week: str
    start_time: str
    end_time: str
    course_name: str


class RoomAvailabilityRead(BaseModel):
    """One room plus the engine's decision about it right now."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    building: str
    room_type: str
    capacity: int
    state: str
    reason: str
    active_class: ActiveClassRead | None = None
    timetable: list[dict] = []


class AvailabilityListResponse(BaseModel):
    """Wrapper so the frontend gets one stable shape (plus handy counts)."""

    evaluated_at: datetime
    count: int
    available_count: int
    in_class_count: int
    rooms: list[RoomAvailabilityRead]
