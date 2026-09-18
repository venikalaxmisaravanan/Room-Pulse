"""Deterministic availability engine for RoomPulse (Stage 3).

This is the "brain" of RoomPulse in its simplest form. It answers one question:

    "Can this room actually be used right now?"

For Stage 3 the engine only knows two things:

1. the room's timetable slots, and
2. the moment we are asking about.

That is enough for exactly two states:

- IN_CLASS  -> a timetable slot for that room is currently active.
- AVAILABLE -> no timetable class is currently in session.

Occupancy sensors, reservations, sensor freshness and WebSocket updates do not
exist yet, so OCCUPIED / RESERVED / FULL / UNKNOWN are *not* produced here.
They are listed as FUTURE_STATES below so later stages can reuse the same
vocabulary without pretending Stage 3 knows more than it does.

Design rules this module follows:

- The core function `decide()` is a pure function: it never reads the clock,
  the database or any global state. The caller passes `now` in, which makes
  the function deterministic and easy to test with fixed datetimes.
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

# States this stage actually produces.
AVAILABLE = "AVAILABLE"
IN_CLASS = "IN_CLASS"

# States reserved for later stages (occupancy simulator, reservations,
# sensor freshness). Listed here only so the whole project shares one
# vocabulary; the engine below never returns them.
FUTURE_STATES = ("OCCUPIED", "RESERVED", "FULL", "UNKNOWN")

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
    slots: Iterable[SlotLike | dict], now: datetime
) -> AvailabilityDecision:
    """Decide AVAILABLE vs IN_CLASS for one room's slots at one moment.

    ``slots`` is the room's timetable (possibly empty); ``now`` is the moment
    being evaluated. A room with no active slot is AVAILABLE — an empty
    timetable never means "busy".
    """
    active = find_active_slot(slots, now)
    if active is None:
        return AvailabilityDecision(
            state=AVAILABLE,
            reason="No class is scheduled right now.",
            active_slot=None,
        )
    return AvailabilityDecision(
        state=IN_CLASS,
        reason=(
            f"{active.course_name} is in progress "
            f"until {active.end_time.strftime('%H:%M')}."
        ),
        active_slot=active,
    )
