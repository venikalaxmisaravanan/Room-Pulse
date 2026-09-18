"""Response schemas for the simulated occupancy endpoint.

Like availability, these describe transient sensor input — not rows in
SQLite. Each reading carries its own timestamp so Stage 5 (freshness) can
later compare it against "now"; this stage only prepares the field.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OccupancyReadingRead(BaseModel):
    """One simulated sensor report for one room."""

    model_config = ConfigDict(from_attributes=True)

    room_id: int
    code: str
    occupancy: int
    capacity: int
    scenario: str
    timestamp: datetime
    simulated: bool = True


class OccupancyListResponse(BaseModel):
    """Wrapper so the frontend gets one stable shape."""

    evaluated_at: datetime
    count: int
    readings: list[OccupancyReadingRead]
