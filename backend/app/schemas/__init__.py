"""Pydantic models describing what the API sends and receives.

Today that is the health response, the room catalogue and the derived
availability answers. Reservation and occupancy schemas arrive with their
stages.
"""

from app.schemas.availability import (
    ActiveClassRead,
    AvailabilityListResponse,
    OccupancyRead,
    RoomAvailabilityRead,
)
from app.schemas.health import HealthResponse
from app.schemas.occupancy import OccupancyListResponse, OccupancyReadingRead
from app.schemas.room import RoomListResponse, RoomRead, TimetableSlotRead

__all__ = [
    "ActiveClassRead",
    "AvailabilityListResponse",
    "HealthResponse",
    "OccupancyListResponse",
    "OccupancyRead",
    "OccupancyReadingRead",
    "RoomAvailabilityRead",
    "RoomListResponse",
    "RoomRead",
    "TimetableSlotRead",
]