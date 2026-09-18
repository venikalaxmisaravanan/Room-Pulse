"""Pydantic models describing what the API sends and receives.

Room, timetable and reservation schemas will be added here later. Today there
is only the health response.
"""

from app.schemas.health import HealthResponse

__all__ = ["HealthResponse"]