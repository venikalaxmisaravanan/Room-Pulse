"""Application logic.

The availability engine (Stage 3) lives here alongside the room catalogue
reader, so route handlers stay thin and easy to read. The occupancy
simulator and sensor-freshness rules arrive with their own stages.
"""

from app.services.availability import AVAILABLE, IN_CLASS, AvailabilityDecision, decide
from app.services.availability_service import evaluate_catalogue
from app.services.room_service import list_rooms_with_timetable

__all__ = [
    "AVAILABLE",
    "IN_CLASS",
    "AvailabilityDecision",
    "decide",
    "evaluate_catalogue",
    "list_rooms_with_timetable",
]