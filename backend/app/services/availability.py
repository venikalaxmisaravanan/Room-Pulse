"""Deterministic availability engine for RoomPulse (Stage 4).

This is the "brain" of RoomPulse. It answers one question:

    "Can this room actually be used right now?"

The engine now knows three things:

1. the room's timetable slots,
2. the moment we are asking about, and
3. the simulated occupancy reading for the room (people detected inside).

That produces four states with this explicit precedence (checked top-down):

1. FULL      -> occupancy has reached room capacity. Nobody else fits,
   regardless of what the timetable says.
2. IN_CLASS  -> a timetable slot is currently active. The class wins over a
   headcount: a scheduled class owns the room even if the sensor has not
   caught up yet.
3. OCCUPIED  -> people are physically detected (occupancy > 0) while no
   class is scheduled. The room looks free on paper but is not free in fact.
4. AVAILABLE -> no class scheduled and nobody detected.

OCCUPIED is deliberately defined as "people present *outside* a scheduled
class". When a class is in session, IN_CLASS already explains the room, so
OCCUPIED never needs to compete with it.

RESERVED and UNKNOWN are still future vocabulary (reservations, sensor
freshness in later stages); the engine below never returns them.

Design rules this module follows:

- The core function `decide()` is a pure function: it never reads the clock,
  the database or any global state. The caller passes `now` (and the
  occupancy) in, which makes the function deterministic and easy to test.
- Boundary convention: start time is inclusive, end time is exclusive.
  A class from 11:30 to 13:00 is active at 11:30 but not at exactly 13:00.
- Weekday mapping is explicit: Python's ``datetime.weekday()`` (Monday == 0)
  is mapped through the WEEKDAY_NAMES tuple below, not through fragile
  string comparisons.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Iterable, Protocol

# States this stage produces, in precedence order (highest first).
FULL = "FULL"
IN_CLASS = "IN_CLASS"
OCCUPIED = "OCCUPIED"
AVAILABLE = "AVAILABLE"

# States reserved for later stages (reservations, sensor freshness). Listed
# here only so the whole project shares one vocabulary; the engine below
# never returns them.
FUTURE_STATES = ("RESERVED", "UNKNOWN")

# Monday-first, matching datetime.weekday() where Monday == 0.
# Sunday is included so "different weekday -> AVAILABLE" is well defined.
WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class SlotLike(Protocol):
    """Anything with the four fields the engine needs.

    This covers the SQLAlchemy TimetableSlot rows, the pydantic
    TimetableSlotRead objects and the plain dicts used in tests.
    ``start_time`` / ``end_time`` may be datetime.time or "HH:MM" strings.
    """

    day_of_week: str
    start_time: object
    end_time: object
    course_name: str


@dataclass(frozen=True)
class SlotView:
    """A normalised copy of one timetable slot the engine can compare."""

    day_of_week: str
    start_time: time
    end_time: time
    course_name: str


@dataclass(frozen=True)
class AvailabilityDecision:
    """The engine's answer for one room at one moment."""

    state: str
    reason: str
    active_slot: SlotView | None = None


def _coerce_time(value: time | str) -> time:
    """Accept a time object or an "HH:MM[:SS]" string, return a time object."""
    if isinstance(value, time):
        return value
    return time.fromisoformat(str(value))


def _normalise_slot(slot: SlotLike | dict) -> SlotView:
    """Turn any slot-shaped object into a SlotView with real time objects."""
    if isinstance(slot, dict):
        day = slot["day_of_week"]
        start = slot["start_time"]
        end = slot["end_time"]
        course = slot["course_name"]
    else:
        day = slot.day_of_week  # type: ignore[union-attr]
        start = slot.start_time  # type: ignore[union-attr]
        end = slot.end_time  # type: ignore[union-attr]
        course = slot.course_name  # type: ignore[union-attr]
    return SlotView(
        day_of_week=str(day),
        start_time=_coerce_time(start),
        end_time=_coerce_time(end),
        course_name=str(course),
    )


def _weekday_name(now: datetime) -> str:
    """Map a datetime to its weekday name through an explicit table."""
    return WEEKDAY_NAMES[now.weekday()]


def find_active_slot(
    slots: Iterable[SlotLike | dict], now: datetime
) -> SlotView | None:
    """Return the timetable slot in session at ``now``, or None.

    A slot is active when its weekday matches today and
    ``start_time <= now.time() < end_time``.
    When overlapping slots are somehow active at once, the one that
    started earliest wins so the answer stays deterministic.
    """
    today = _weekday_name(now)
    current = now.time()
    candidates = [
        _normalise_slot(slot)
        for slot in slots
        if _normalise_slot(slot).day_of_week == today
        and _normalise_slot(slot).start_time <= current
        < _normalise_slot(slot).end_time
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda slot: (slot.start_time, slot.end_time))


def decide(
    slots: Iterable[SlotLike | dict],
    now: datetime,
    occupancy: int = 0,
    capacity: int = 0,
) -> AvailabilityDecision:
    """Decide FULL / IN_CLASS / OCCUPIED / AVAILABLE for one room at ``now``.

    ``slots`` is the room's timetable (possibly empty); ``occupancy`` is the
    simulated headcount (defaults to 0 so old Stage 3 calls keep working);
    ``capacity`` is the room's seat count. Precedence, checked top-down:

    1. FULL when 0 < capacity <= occupancy (occupancy is clamped into range
       first, so a weird input can never produce FULL by accident);
    2. IN_CLASS when a timetable slot covers ``now``;
    3. OCCUPIED when occupancy > 0 but no class is scheduled;
    4. AVAILABLE otherwise — including a room with no timetable at all.
    """
    occupancy = max(0, occupancy)
    if capacity > 0:
        occupancy = min(occupancy, capacity)

    active = find_active_slot(slots, now)
    if capacity > 0 and occupancy >= capacity:
        return AvailabilityDecision(
            state=FULL,
            reason=(
                f"The room is full ({occupancy}/{capacity} people)"
                + (
                    f" — {active.course_name} is in session."
                    if active is not None
                    else "."
                )
            ),
            active_slot=active,
        )
    if active is not None:
        return AvailabilityDecision(
            state=IN_CLASS,
            reason=(
                f"{active.course_name} is in progress "
                f"until {active.end_time.strftime('%H:%M')}."
            ),
            active_slot=active,
        )
    if occupancy > 0:
        return AvailabilityDecision(
            state=OCCUPIED,
            reason=(
                f"{occupancy} "
                f"{'person' if occupancy == 1 else 'people'} "
                "detected in the room (simulated sensor), "
                "no class is scheduled."
            ),
            active_slot=None,
        )
    return AvailabilityDecision(
        state=AVAILABLE,
        reason="No class is scheduled and the room looks empty.",
        active_slot=None,
    )
