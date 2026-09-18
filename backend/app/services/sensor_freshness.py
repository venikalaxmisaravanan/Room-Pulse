"""Sensor freshness for RoomPulse (Stage 5).

RoomPulse does not blindly trust an old sensor reading. Every occupancy
reading carries a timestamp; this module compares that timestamp against the
moment we are evaluating and decides whether the reading should influence the
room's availability.

The rule is intentionally simple and deterministic:

- a reading is **fresh** when its age is at most ``threshold_seconds``;
- a reading is **stale** when its age is greater than ``threshold_seconds``.

The boundary is inclusive on the fresh side, so an age that lands exactly on
the threshold is still trusted — this keeps the common demo case simple and
the "exactly at the limit" rule easy to reason about.

There is no background job, no WebSocket stream and no storage of freshness
decisions here. Freshness is a transient decision made inside the availability
endpoint at the moment of evaluation, the same way the timetable comparison
is made.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class ReadingLike(Protocol):
    """Anything that looks like one occupancy reading for freshness purposes.

    ``timestamp`` may be a ``datetime`` or an ISO timestamp string; the helper
    normalises it so tests can pass plain dicts.
    """

    occupancy: object
    capacity: object
    scenario: object
    timestamp: object
    simulated: object


@dataclass(frozen=True)
class ReadingFreshness:
    """The freshness verdict for one reading at one evaluation moment."""

    # One of ``FRESH``, ``STALE``, ``NO_READING``.
    status: str
    # Age of the reading in seconds, rounded down. ``0`` when there is no
    # reading or the reading is from the future relative to ``evaluated_at``.
    age_seconds: int
    fresh: bool
    # Human-readable line for the dashboard and the reason text.
    sensor_note: str


def _as_datetime(value: datetime | str) -> datetime:
    """Accept a datetime or an ISO string, return a datetime."""
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def assess_reading(
    reading: ReadingLike | None,
    evaluated_at: datetime,
    threshold_seconds: int,
) -> ReadingFreshness:
    """Decide whether one reading is fresh at ``evaluated_at``.

    Returns ``NO_READING`` when ``reading`` is falsy (``None`` etc.), because
    an absent reading cannot be trusted and a later stage may want to treat it
    as unknown rather than assume a default occupancy.
    """
    if not reading:
        return ReadingFreshness(
            status="NO_READING",
            age_seconds=0,
            fresh=False,
            sensor_note="Sensor reading is missing entirely.",
        )

    ts = _as_datetime(reading.timestamp)
    age_seconds = max(0, int((evaluated_at - ts).total_seconds()))

    if age_seconds <= threshold_seconds:
        note = (
            f"Sensor reading is fresh (last update {age_seconds}s ago)."
        )
        return ReadingFreshness(
            status="FRESH",
            age_seconds=age_seconds,
            fresh=True,
            sensor_note=note,
        )

    # Age strictly greater than the threshold.
    minutes = age_seconds // 60
    seconds = age_seconds % 60
    if minutes:
        time_str = f"{minutes}m {seconds}s ago"
    else:
        time_str = f"{seconds}s ago"
    note = (
        f"Sensor reading is stale (last update {time_str}, older than "
        f"{threshold_seconds}s). RoomPulse will not trust this reading for "
        "availability."
    )
    return ReadingFreshness(
        status="STALE",
        age_seconds=age_seconds,
        fresh=False,
        sensor_note=note,
    )


__all__ = [
    "ReadingFreshness",
    "ReadingLike",
    "assess_reading",
    "assess_reading",
]