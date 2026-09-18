"""Room availability endpoint (read-only, derived — never stored).

The route does three boring things: load rooms, ask "what time is it?", and
return the engine's answer. All decision rules live in
``app.services.availability`` so they can be unit-tested without HTTP.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.availability import AvailabilityListResponse
from app.services.availability_service import evaluate_catalogue

router = APIRouter(tags=["availability"])


@router.get(
    "/rooms/availability",
    response_model=AvailabilityListResponse,
    summary="Current AVAILABLE / IN_CLASS state of every room",
)
def get_rooms_availability(
    db: Session = Depends(get_db),
    at: str | None = Query(
        default=None,
        description=(
            "Optional ISO datetime to evaluate instead of now, "
            "e.g. 2026-09-21T12:00:00. Useful for demos and debugging; "
            "the dashboard omits it so it always sees the live answer."
        ),
    ),
) -> AvailabilityListResponse:
    """Derive each room's state from its timetable at one moment.

    ``at`` is intentionally a plain string parameter: when it is absent the
    server clock is used, when it is present it must parse as an ISO
    datetime, otherwise the request fails with a clear 400-style error.
    """
    if at is None:
        now = datetime.now()
    else:
        try:
            now = datetime.fromisoformat(at)
        except ValueError as exc:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Query parameter 'at' is not a valid ISO datetime: {at!r}",
            ) from exc
    return evaluate_catalogue(db, now)
