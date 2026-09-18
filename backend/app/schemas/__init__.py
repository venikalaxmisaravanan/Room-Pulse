"""Pydantic models describing what the API sends and receives.

Today that is the health response and the room catalogue. Reservation and
occupancy schemas arrive with their stages.
"""

from app.schemas.health import HealthResponse
from app.schemas.room import RoomListResponse, RoomRead, TimetableSlotRead

__all__ = [
    "HealthResponse",
    "RoomListResponse",
    "RoomRead",
    "TimetableSlotRead",
]