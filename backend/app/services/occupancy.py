"""Simulated occupancy sensor for RoomPulse (Stage 4).

There are no physical sensors or cameras in this prototype, so this module
pretends to be the sensor layer. It produces one reading per room:

    { room_id, code, occupancy, capacity, scenario, timestamp }

Design rules:

- Room catalogue = stable input (SQLite). Occupancy = changing sensor input.
  Availability = derived result. Nothing here writes to the database, and the
  Room table gains no occupancy/status columns.
- Readings are deterministic functions of (room code, capacity, time), so
  tests with fixed datetimes always get the same answer. No uncontrolled
  randomness anywhere.
- Every reading carries its own timestamp. Stage 5 (sensor freshness) will
  compare that timestamp against "now" — this stage only prepares the field.
- SENSOR_FAILURE rooms freeze: the first call stores a reading and later
  calls return the *same object with the original timestamp*, so Stage 5 can
  later notice the timestamp has gone old. No fresh timestamp is faked.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

# Scenario names. ROOM_EMPTYING keeps the spec's vocabulary.
NORMAL = "NORMAL"
CROWDING = "CROWDING"
ROOM_EMPTYING = "ROOM_EMPTYING"
SUDDEN_OCCUPANCY = "SUDDEN_OCCUPANCY"
SENSOR_FAILURE = "SENSOR_FAILURE"

SCENARIOS = (NORMAL, CROWDING, ROOM_EMPTYING, SUDDEN_OCCUPANCY, SENSOR_FAILURE)

# The simulator "ticks" every 2 minutes: readings change over time, but two
# calls inside the same tick return the same occupancy (deterministic).
STEP_SECONDS = 120

# Occupancy expressed as a fraction of room capacity per tick. Each list is
# one full cycle; rooms start at different offsets so they do not move
# in lockstep.
LEVELS: dict[str, list[float]] = {
    # Gradual drift up and down: 15 -> 18 -> 22 -> 25 -> 21 style.
    NORMAL: [0.20, 0.25, 0.30, 0.35, 0.30, 0.25],
    # Climbs until the room is full (last level == 1.0).
    CROWDING: [0.30, 0.50, 0.65, 0.80, 0.90, 1.0],
    # Drains away: 52 -> 38 -> 21 -> 8 -> 2 style.
    ROOM_EMPTYING: [0.90, 0.70, 0.45, 0.20, 0.10, 0.05],
    # Quiet, quiet, quiet, then suddenly busy.
    SUDDEN_OCCUPANCY: [0.10, 0.12, 0.15, 0.70, 0.80, 0.75],
    # Unused for live values (failure rooms freeze instead), but kept so the
    # table stays total over SCENARIOS.
    SENSOR_FAILURE: [0.20],
}

# Fixed scenario per seeded room, so every scenario is visible on the
# dashboard and demos are repeatable. Any unknown room falls back to NORMAL.
SCENARIO_BY_CODE: dict[str, str] = {
    "EN-101": NORMAL,
    "EN-102": CROWDING,
    "EN-L1": ROOM_EMPTYING,
    "SC-115": SUDDEN_OCCUPANCY,
    "SC-210": NORMAL,
    "SC-L2": CROWDING,
    "BS-104": ROOM_EMPTYING,
    "BS-301": SENSOR_FAILURE,
    "BS-L3": NORMAL,
}


@dataclass(frozen=True)
class OccupancyReading:
    """One simulated sensor report for one room at one moment."""

    room_id: int
    code: str
    occupancy: int
    capacity: int
    scenario: str
    timestamp: datetime
    simulated: bool = True


# Frozen readings for SENSOR_FAILURE rooms: room_id -> first-ever reading.
# In-memory on purpose (sensor state is transient, not catalogue data).
_FROZEN: dict[int, OccupancyReading] = {}
_LIVE_NOW: datetime | None = None


def assign_scenario(code: str) -> str:
    """Return the deterministic scenario for a room code."""
    return SCENARIO_BY_CODE.get(code, NORMAL)


def _tick(now: datetime) -> int:
    """Monotonic tick number: changes every STEP_SECONDS, deterministic."""
    return int(now.timestamp() // STEP_SECONDS)


def _offset(code: str, length: int) -> int:
    """Deterministic per-room offset so rooms do not move in lockstep."""
    return sum(ord(char) for char in code) % length


def occupancy_for(code: str, capacity: int, scenario: str, now: datetime) -> int:
    """Deterministic occupancy for a room at a moment, always 0..capacity."""
    if capacity <= 0:
        return 0
    levels = LEVELS.get(scenario, LEVELS[NORMAL])
    fraction = levels[(_tick(now) + _offset(code, len(levels))) % len(levels)]
    # int() floors, so CROWDING's 1.0 lands exactly on capacity (FULL) and
    # nothing can exceed it; max() guards tiny capacities against negatives.
    return max(0, min(capacity, int(fraction * capacity)))


def reset_simulator() -> None:
    """Clear frozen SENSOR_FAILURE readings (tests and demos only)."""
    _FROZEN.clear()


def init_occupancy_jsim_for_loop() -> None:
    """Start the live simulator clock without changing its reading rules."""
    global _LIVE_NOW
    _LIVE_NOW = datetime.now()


def advance_simulation_one_tick() -> None:
    """Advance the existing deterministic simulator by one configured tick."""
    global _LIVE_NOW
    if _LIVE_NOW is None:
        init_occupancy_jsim_for_loop()
    _LIVE_NOW += timedelta(seconds=STEP_SECONDS)


def current_evaluated_at() -> datetime:
    """Return the live simulator's current evaluation moment."""
    if _LIVE_NOW is None:
        init_occupancy_jsim_for_loop()
    return _LIVE_NOW


def reading_for(
    room_id: int, code: str, capacity: int, now: datetime
) -> OccupancyReading:
    """Build the current reading for one room.

    SENSOR_FAILURE rooms return their frozen first reading forever (same
    occupancy, same original timestamp) — the "sensor" has gone silent.
    """
    scenario = assign_scenario(code)
    if scenario == SENSOR_FAILURE:
        frozen = _FROZEN.get(room_id)
        if frozen is None:
            frozen = OccupancyReading(
                room_id=room_id,
                code=code,
                occupancy=occupancy_for(code, capacity, NORMAL, now),
                capacity=capacity,
                scenario=scenario,
                timestamp=now,
            )
            _FROZEN[room_id] = frozen
        return frozen
    return OccupancyReading(
        room_id=room_id,
        code=code,
        occupancy=occupancy_for(code, capacity, scenario, now),
        capacity=capacity,
        scenario=scenario,
        timestamp=now,
    )


def current_readings(rooms, now: datetime) -> list[OccupancyReading]:
    """Build the current reading for every room in the catalogue."""
    return [
        reading_for(room.id, room.code, room.capacity, now) for room in rooms
    ]


__all__ = [
    "CROWDING",
    "LEVELS",
    "NORMAL",
    "ROOM_EMPTYING",
    "SCENARIOS",
    "SCENARIO_BY_CODE",
    "SENSOR_FAILURE",
    "STEP_SECONDS",
    "SUDDEN_OCCUPANCY",
    "OccupancyReading",
    "assign_scenario",
    "current_readings",
    "current_evaluated_at",
    "advance_simulation_one_tick",
    "init_occupancy_jsim_for_loop",
    "occupancy_for",
    "reading_for",
    "reset_simulator",
]