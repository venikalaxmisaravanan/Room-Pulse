"""The TimetableSlot table: scheduled class usage of a room."""

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.room import Room


# Ordered Monday-first, so the API can sort slots the way a student reads a
# timetable. The names match `datetime.date.strftime("%A")`, which the
# availability engine will use later to find "is a class scheduled right now?".
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")


class TimetableSlot(Base):
    """One scheduled class session in one room.

    The timetable is only *one* input for the availability engine. Nothing here
    marks a room as busy or free yet: turning timetable + occupancy +
    reservations + sensor freshness into a single room state is engine work for
    a later stage.
    """

    __tablename__ = "timetable_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    day_of_week: Mapped[str] = mapped_column(String(9), index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    course_name: Mapped[str] = mapped_column(String(80))

    room: Mapped["Room"] = relationship(back_populates="timetable")

    def __repr__(self) -> str:
        return (
            f"<TimetableSlot {self.day_of_week} "
            f"{self.start_time:%H:%M}-{self.end_time:%H:%M} {self.course_name}>"
        )
