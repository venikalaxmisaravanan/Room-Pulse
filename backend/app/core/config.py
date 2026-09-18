"""Application configuration for RoomPulse.

This stage needs almost nothing: just the values the API uses to describe
itself in the health response. Keeping them in one module means later stages
(SQLite path, simulator interval, WebSocket settings) have one obvious home.
"""

import os

APP_NAME = "RoomPulse API"
APP_DESCRIPTION = "Real-time campus room availability engine."
APP_VERSION = "0.1.0"

# Everything the frontend calls lives under this prefix, e.g. /api/health.
API_PREFIX = "/api"

# Handy for debugging and for the dashboard status line. Override with the
# ROOMPULSE_ENV environment variable if you ever need to.
ENVIRONMENT = os.getenv("ROOMPULSE_ENV", "development")

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
