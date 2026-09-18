"""Room catalogue endpoint (read-only).

There are intentionally no create/update/delete routes in this stage: the
prototype catalogue comes from `app/db/seed_data.py` so that it stays
deterministic, and availability is not stored anywhere.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.room import RoomListResponse
from app.services.room_service import list_rooms_with_timetable

router = APIRouter(tags=["rooms"])


@router.get(
    "/rooms",
    response_model=RoomListResponse,
    summary="List every room and its timetable",
)
def get_rooms(db: Session = Depends(get_db)) -> RoomListResponse:
    """Return the room catalogue from SQLite, timetable slots nested per room.

    No availability information is included, because the availability engine
    does not exist yet. That is why the dashboard shows UNKNOWN for every room.
    """
    rooms = list_rooms_with_timetable(db)
    return RoomListResponse(count=len(rooms), rooms=rooms)
