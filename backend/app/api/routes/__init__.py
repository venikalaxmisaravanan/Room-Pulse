"""API routers.

One file per concern. Later stages add next to these:

- reservations.py -> faculty reservations

Keeping them separate means the availability engine can grow without turning
one giant route file into a mess.
"""

from app.api.routes.availability import router as availability_router
from app.api.routes.health import router as health_router
from app.api.routes.occupancy import router as occupancy_router
from app.api.routes.rooms import router as rooms_router
from app.api.routes.ws import router as ws_router

__all__ = [
    "availability_router",
    "health_router",
    "occupancy_router",
    "rooms_router",
    "ws_router",
]