"""Application logic.

The availability engine, the occupancy simulator and the sensor-freshness rules
will live here so that route handlers stay thin and easy to read. Today it holds
the room catalogue reader.
"""

from app.services.room_service import list_rooms_with_timetable

__all__ = ["list_rooms_with_timetable"]