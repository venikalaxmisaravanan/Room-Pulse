"""Deterministic availability engine for RoomPulse (Stage 4).

This is the "brain" of RoomPulse. It answers one question:

    "Can this room actually be used right now?"

The engine now knows three things:

1. the room's timetable slots,
2. the moment we are asking about, and
3. the simulated occupancy reading for the room (people detected inside).

That produces state vocabulary that now includes UNKNOWN and respects this
precedence (checked top-down):

1. IN_CLASS     -> a timetable slot is currently active. The class wins over
   any occupancy signal, fresh or stale — an active class is the strongest fact
   we have and sensor freshness never removes it.
2. FULL         -> a trusted occupancy reading has reached room capacity.
3. OCCUPIED    -> a trusted occupancy reading is positive while no class is
   scheduled.
4. UNKNOWN      -> no active class and the occupancy signal cannot be trusted
   (stale or missing reading). RoomPulse refuses to pretend the room is free or
   occupied when it does not have a dependable reading.
5. AVAILABLE   -> no class scheduled and nobody detected / no reason to believe
   otherwise.

RESERVED is still future vocabulary (reservations); the engine below may also
return UNKNOWN during sensor-freshness stages.

Design rules this module follows:

- The core function `decide()` is a pure function with respect to the inputs it
  is given: the caller supplies `now`, the occupancy number, and the freshness
  verdict. Nothing in this file reaches the clock, the database or globals, so
  it is easy to test with fixed datetimes.
- Boundary convention: start time is inclusive, end time is exclusive.
  A class from 11:30 to 13:00 is active at 11:30 but not at exactly 13:00.
- Weekday mapping is explicit: Python's ``datetime.weekday()`` (Monday == 0)
  is mapped through the WEEKDAY_NAMES tuple below, not through fragile
  string comparisons.
- Freshness is an external concern. This module only asks ``freshness.fresh``
  whether to trust the occupancy number; the actual staleness threshold and the
  age computation live in ``app.services.sensor_freshness``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Iterable, Protocol

UNKNOWN = "UNKNOWN"

AVAILABLE = "AVAILABLE"
FULL = "FULL"
IN_CLASS = "IN_CLASS"
OCCUPIED = "OCCUPIED"

# States reserved for later stages (reservations). Listed
# here only so the whole project shares one vocabulary; the engine below
# may also return UNKNOWN when the occupancy signal cannot be trusted.
FUTURE_STATES = ("RESERVED",)

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
    freshness: "ReadingFreshness | None" = None,
) -> AvailabilityDecision:
    """Decide FULL / IN_CLASS / OCCUPIED / AVAILABLE / UNKNOWN for one room at
    ``now``.

    ``slots`` is the room's timetable (possibly empty); ``occupancy`` is the
    simulated headcount passed through from the simulator (defaults to 0 so
    old calls keep working); ``capacity`` is the room's seat count.

    ``freshness`` is an optional ``ReadingFreshness`` verdict from
    ``app.services.sensor_freshness.assess_reading``. When the verdict says the
    reading cannot be trusted (e.g. ``STALE`` or ``NO_READING``), the engine
    stops treating the occupancy number as an authoritative fact and may return
    ``UNKNOWN`` instead of OCCUPIED/AVAILABLE. **An active timetable slot is
    never overruled by freshness**: if a class is in session the room is
    ``IN_CLASS`` regardless of how stale the sensor is.

    Precedence, checked top-down:

    1. IN_CLASS when a timetable slot covers ``now`` (class wins over any
       occupancy signal, fresh or stale);
    2. FULL when 0 < capacity <= occupancy, and the occupancy signal is trusted
       (fresh / present);
    3. OCCUPIED when occupancy > 0 and the occupancy signal is trusted;
    4. UNKNOWN when there is no active class and the occupancy signal cannot be
       trusted (stale reading or missing reading);
    5. AVAILABLE otherwise — no class scheduled and nobody detected / no signal
       to the contrary.
    """
    occupancy = max(0, occupancy)
    if capacity > 0:
        occupancy = min(occupancy, capacity)

    active = find_active_slot(slots, now)

    # An active class owns the room independent of sensor freshness. That is the
    # Stage 3 guarantee preserved here: a scheduled class is a stronger fact than
    # a live headcount which may be stale.
    if active is not None:
        return AvailabilityDecision(
            state=IN_CLASS,
            reason=(
                f"{active.course_name} is in progress "
                f"until {active.end_time.strftime('%H:%M')}."
            ),
            active_slot=active,
        )

    # Trust the reading only when freshness says so. When it does not, drop the
    # occupancy number as evidence and move to the stale / missing branch below.
    trusted = freshness is None or freshness.fresh is True

    occupancy = max(0, occupancy)
    if capacity > 0:
        occupancy = min(occupancy, capacity)

    if trusted and capacity > 0 and occupancy >= capacity:
        return AvailabilityDecision(
            state=FULL,
            reason=(
                f"The room is full ({occupancy}/{capacity} people)"
                + (
                    f" — {active.course_name} is in session."
                    if False  # active is None here by this point
                    else "."
                )
            ),
            active_slot=None,
        )

    if trusted and occupancy > 0:
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

    # No active class, and the occupancy signal is not dependable. This is the
    # case freshness exists to catch: a stale or missing reading should not
    # silently turn into AVAILABLE (which claims the room is free) or OCCUPIED
    # (which pretends we know headcount).
    if not trusted:
        if freshness is None or freshness.status == "NO_READING":
            return AvailabilityDecision(
                state=UNKNOWN,
                reason=(
                    "No class is scheduled and the sensor reading is missing, "
                    "so RoomPulse cannot tell whether the room is usable right now."
                ),
                active_slot=None,
            )
        return AvailabilityDecision(
            state=UNKNOWN,
            reason=(
                "No class is scheduled and the sensor reading is stale, "
                "so RoomPulse is not sure whether the room is usable right now."
            ),
            active_slot=None,
        )

    return AvailabilityDecision(
        state=AVAILABLE,
        reason="No class is scheduled and the room looks empty.",
        active_slot=None,
    )


__all__ = [
    "AVAILABLE",
    "FULL",
    "IN_CLASS",
    "OCCUPIED",
    "UNKNOWN",
    "AvailabilityDecision",
    "FUTURE_STATES",
    "SlotLike",
    "SlotView",
    "WEEKDAY_NAMES",
    "decide",
    "find_active_slot",
    "ReadingFreshness",
]
