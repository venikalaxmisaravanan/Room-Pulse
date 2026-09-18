"""API routers.

One file per concern. Later stages add next to these:

- availability.py -> what the availability engine decided
- occupancy.py    -> live occupancy readings
- reservations.py -> faculty reservations

Keeping them separate means the availability engine can grow without turning
one giant route file into a mess.
"""

from app.api.routes.health import router as health_router
from app.api.routes.rooms import router as rooms_router

__all__ = ["health_router", "rooms_router"]