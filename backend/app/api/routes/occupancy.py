"""Simulated occupancy endpoint (read-only, transient — never stored).

The route loads the room catalogue, asks the simulator for the current
reading of every room at one moment, and returns the reports. Like
availability, occupancy is sensor input: it lives in memory, not in SQLite.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Room
from app.schemas.occupancy import OccupancyListResponse, OccupancyReadingRead
from app.services.occupancy import current_readings

router = APIRouter(tags=["occupancy"])


@router.get(
    "/rooms/occupancy",
    response_model=OccupancyListResponse,
    summary="Current simulated occupancy reading of every room",
)
def get_rooms_occupancy(
    db: Session = Depends(get_db),
    at: str | None = Query(
        default=None,
        description=(
            "Optional ISO datetime to evaluate instead of now, "
            "e.g. 2026-09-21T12:00:00. Useful for demos and debugging; "
            "the dashboard omits it so it always sees the live answer."
        ),
    ),
) -> OccupancyListResponse:
    """Return one simulated sensor report per room at one moment."""
    if at is None:
        now = datetime.now()
    else:
        try:
            now = datetime.fromisoformat(at)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Query parameter 'at' is not a valid ISO datetime: {at!r}",
            ) from exc

    rooms = db.scalars(select(Room).order_by(Room.code)).all()
    readings = current_readings(rooms, now)
    return OccupancyListResponse(
        evaluated_at=now,
        count=len(readings),
        readings=[
            OccupancyReadingRead(
                room_id=reading.room_id,
                code=reading.code,
                occupancy=reading.occupancy,
                capacity=reading.capacity,
                scenario=reading.scenario,
                timestamp=reading.timestamp,
                simulated=reading.simulated,
            )
            for reading in readings
        ],
    )
