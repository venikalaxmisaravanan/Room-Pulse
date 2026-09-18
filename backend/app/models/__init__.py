"""SQLAlchemy models.

Importing this package registers every table on `Base.metadata`, which is what
`create_all()` needs in order to build the SQLite file. Add new tables to the
imports below when they appear.
"""

from app.models.room import ROOM_TYPES, Room
from app.models.timetable import WEEKDAYS, TimetableSlot

__all__ = ["ROOM_TYPES", "WEEKDAYS", "Room", "TimetableSlot"]
