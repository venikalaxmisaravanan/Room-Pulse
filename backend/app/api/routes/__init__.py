"""API routers.

Only the health router exists in this stage. Later stages add one file per
concern next to it, for example:

- rooms.py        -> the room catalogue
- availability.py -> what the availability engine decided
- occupancy.py    -> live occupancy readings
- timetable.py    -> class schedules
- reservations.py -> faculty reservations

Keeping them separate means the availability engine can grow without turning
one giant route file into a mess.
"""

from app.api.routes.health import router as health_router

__all__ = ["health_router"]