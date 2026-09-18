"""Response schemas for the room catalogue.

These describe the exact JSON the dashboard receives. Notice there is no
availability/status field anywhere: that value does not exist yet, and inventing
one here would make the API lie about what it knows.
"""

from datetime import time

from pydantic import BaseModel, ConfigDict


class TimetableSlotRead(BaseModel):
    """One scheduled class session, nested inside its room."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    day_of_week: str
    start_time: time
    end_time: time
    course_name: str


class RoomRead(BaseModel):
    """A room from the catalogue, with the timetable slots that belong to it."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    building: str
    room_type: str
    capacity: int
    timetable: list[TimetableSlotRead]


class RoomListResponse(BaseModel):
    """Wrapper so the frontend gets one stable shape (plus a handy count)."""

    count: int
    rooms: list[RoomRead]