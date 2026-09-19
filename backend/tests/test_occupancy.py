"""Focused tests for deterministic simulated occupancy scenarios."""

from datetime import datetime, timedelta

from app.services.occupancy import (
    LEVELS,
    ROOM_EMPTYING,
    STEP_SECONDS,
    advance_simulation_one_tick,
    current_evaluated_at,
    init_occupancy_jsim_for_loop,
    occupancy_for,
)


def test_room_emptying_can_reach_zero_occupancy():
    start = datetime(2026, 9, 19, 0, 0)
    readings = [
        occupancy_for(
            "EN-L1",
            35,
            ROOM_EMPTYING,
            start + timedelta(seconds=STEP_SECONDS * step),
        )
        for step in range(len(LEVELS[ROOM_EMPTYING]))
    ]

    assert 0 in readings


def test_live_simulator_clock_advances_by_one_step():
    init_occupancy_jsim_for_loop()
    before = current_evaluated_at()

    advance_simulation_one_tick()

    assert current_evaluated_at() - before == timedelta(seconds=STEP_SECONDS)


def test_occupancy_changes_between_simulated_snapshots():
    first = datetime(2026, 9, 19, 0, 0)
    second = first + timedelta(seconds=STEP_SECONDS)

    assert occupancy_for("EN-L1", 35, ROOM_EMPTYING, first) != occupancy_for(
        "EN-L1", 35, ROOM_EMPTYING, second
    )