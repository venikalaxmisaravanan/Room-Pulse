"""Application logic.

The availability engine (Stages 3–4) lives here alongside the room catalogue
reader and the simulated occupancy sensor, so route handlers stay thin and
easy to read. Sensor-freshness rules arrive with their own stage.
"""

from app.services.availability import (
    AVAILABLE,
    FULL,
    IN_CLASS,
    OCCUPIED,
    AvailabilityDecision,
    decide,
)
from app.services.availability_service import evaluate_catalogue
from app.services.occupancy import (
    CROWDING,
    NORMAL,
    ROOM_EMPTYING,
    SCENARIOS,
    SENSOR_FAILURE,
    SUDDEN_OCCUPANCY,
    OccupancyReading,
    current_readings,
    occupancy_for,
    reading_for,
    reset_simulator,
)
from app.services.room_service import list_rooms_with_timetable

__all__ = [
    "AVAILABLE",
    "CROWDING",
    "FULL",
    "IN_CLASS",
    "NORMAL",
    "OCCUPIED",
    "ROOM_EMPTYING",
    "SCENARIOS",
    "SENSOR_FAILURE",
    "SUDDEN_OCCUPANCY",
    "AvailabilityDecision",
    "OccupancyReading",
    "current_readings",
    "decide",
    "evaluate_catalogue",
    "list_rooms_with_timetable",
    "occupancy_for",
    "reading_for",
    "reset_simulator",
]