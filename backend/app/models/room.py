"""The Room table: the physical rooms RoomPulse knows about."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.timetable import TimetableSlot


# The room types used by the prototype data. Stored as plain text so the list
# can grow without touching the database schema.
ROOM_TYPES = (
    "Classroom",
    "Computer Laboratory",
    "Electronics Laboratory",
    "Seminar Room",
)


class Room(Base):
    """A room in a campus building.

    Note what is deliberately missing: there is no `available`, no
    `current_status`, no `occupied` and no `is_free` column. Those are derived
    from timetable + occupancy + reservations + sensor freshness by the
    availability engine in a later stage. Storing them would only create a
    second version of the truth that goes stale immediately.
    """

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    building: Mapped[str] = mapped_column(String(60), index=True)
    room_type: Mapped[str] = mapped_column(String(40), index=True)
    capacity: Mapped[int] = mapped_column(Integer)

    # One room has many timetable slots. `order_by` keeps the loaded list in a
    # stable order; the API sorts by weekday as well (see room_service).
    timetable: Mapped[list["TimetableSlot"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="TimetableSlot.id",
    )

    def __repr__(self) -> str:
        return f"<Room {self.code} ({self.building}, {self.capacity} seats)>"
