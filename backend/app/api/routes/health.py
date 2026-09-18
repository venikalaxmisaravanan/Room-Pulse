"""Health endpoint.

The smallest useful endpoint: it proves the API process is alive so the
dashboard can show a real connection status instead of a decorative light.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import APP_NAME, APP_VERSION, ENVIRONMENT
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Is the API running?")
def get_health() -> HealthResponse:
    """Return a small JSON document confirming the backend is up."""
    return HealthResponse(
        status="ok",
        service=APP_NAME,
        version=APP_VERSION,
        environment=ENVIRONMENT,
        checked_at=datetime.now(timezone.utc),
    )
