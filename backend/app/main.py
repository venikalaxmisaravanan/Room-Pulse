"""RoomPulse API entry point.

Start it with (from the ``backend`` folder):

    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health_router
from app.core.config import (
    API_PREFIX,
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    CORS_ORIGINS,
)

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# The dashboard is served from a different origin during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Every router is mounted under /api so the frontend has one predictable base.
# Availability, occupancy, timetable and reservation routers are added here in
# the next stages.
app.include_router(health_router, prefix=API_PREFIX)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Signpost for anyone who opens the bare API URL in a browser."""
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }