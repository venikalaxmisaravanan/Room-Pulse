"""Response schema for the health endpoint."""

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Shape of the JSON returned by ``GET /api/health``."""

    status: str
    service: str
    version: str
    environment: str
    checked_at: datetime
