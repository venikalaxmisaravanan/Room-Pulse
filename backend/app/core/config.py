"""Application configuration for RoomPulse.

Keeping the handful of values the app needs in one module means later stages
(simulator interval, WebSocket settings) have one obvious home.
"""

import os
from pathlib import Path

APP_NAME = "RoomPulse API"
APP_DESCRIPTION = "Real-time campus room availability engine."
APP_VERSION = "0.2.0"

# Everything the frontend calls lives under this prefix, e.g. /api/health.
API_PREFIX = "/api"

# Handy for debugging and for the dashboard status line. Override with the
# ROOMPULSE_ENV environment variable if you ever need to.
ENVIRONMENT = os.getenv("ROOMPULSE_ENV", "development")

# The backend folder (this file lives in backend/app/core/config.py).
BACKEND_DIR = Path(__file__).resolve().parents[2]

# SQLite is a single local file, which is all a one-day prototype needs. The
# file is created automatically on startup and is ignored by Git.
DATABASE_PATH = Path(
    os.getenv("ROOMPULSE_DB_PATH", str(BACKEND_DIR / "roompulse.db"))
)
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# The React dev server runs on its own origin, so the browser would normally
# block the request. The Vite proxy avoids that for the usual workflow; this
# list keeps direct calls (browser tab, curl, another tool) working too.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ROOMPULSE_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

# Stage 5 (sensor freshness): how old an occupancy reading can be before RoomPulse
# stops trusting it. The value is in seconds and can be overridden with
# ROOMPULSE_SENSOR_FRESHNESS_SECONDS. For the prototype a small value makes
# freshness easy to demonstrate deterministically; the dashboard uses "?at="
# timestamps to reproduce stale readings without waiting around.
SENSOR_FRESHNESS_SECONDS = int(
    os.getenv("ROOMPULSE_SENSOR_FRESHNESS_SECONDS", "30")
)

WS_UPDATE_INTERVAL_SECONDS = float(
    os.getenv("ROOMPULSE_WS_UPDATE_INTERVAL_SECONDS", "5")
)

__all__ = [
    "APP_NAME",
    "APP_DESCRIPTION",
    "APP_VERSION",
    "API_PREFIX",
    "BACKEND_DIR",
    "CORS_ORIGINS",
    "DATABASE_PATH",
    "DATABASE_URL",
    "ENVIRONMENT",
    "SENSOR_FRESHNESS_SECONDS",
    "WS_UPDATE_INTERVAL_SECONDS",
]
