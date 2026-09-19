"""Current usable-room search built on the existing availability snapshot."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.availability import AvailabilityListResponse
from app.services.availability_service import evaluate_catalogue, find_usable_rooms

router = APIRouter(tags=["availability"])


@router.get(
    "/rooms/find",
    response_model=AvailabilityListResponse,
    summary="Find rooms currently usable and matching catalogue requirements",
)
def find_rooms(
    db: Session = Depends(get_db),
    building: str | None = Query(default=None),
    room_type: str | None = Query(default=None),
    min_capacity: int | None = Query(default=None, ge=0),
    seats_needed: int = Query(default=1, ge=1),
    at: str | None = Query(default=None),
) -> AvailabilityListResponse:
    """Return rooms that can accommodate the requested student group."""
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
    snapshot = evaluate_catalogue(db, now)
    return find_usable_rooms(
        snapshot, building, room_type, min_capacity, seats_needed
    )