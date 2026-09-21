"""Focused tests for deterministic simulated occupancy scenarios."""

from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.occupancy import (
    LEVELS,
    ROOM_EMPTYING,
    STEP_SECONDS,
    advance_simulation_one_tick,
    current_evaluated_at,
    current_readings,
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


def test_active_class_keeps_attendance_stable_throughout_the_interval():
    room = SimpleNamespace(
        id=101,
        code="BS-104",
        capacity=70,
        timetable=[
            {
                "day_of_week": "Monday",
                "start_time": "11:00",
                "end_time": "12:00",
                "course_name": "Prototype Lab",
            }
        ],
    )

    values = [
        current_readings([room], datetime(2026, 9, 21, 11, 0, 0))[0].occupancy,
        current_readings([room], datetime(2026, 9, 21, 11, 2, 0))[0].occupancy,
        current_readings([room], datetime(2026, 9, 21, 11, 30, 0))[0].occupancy,
        current_readings([room], datetime(2026, 9, 21, 11, 58, 0))[0].occupancy,
    ]

    assert len(set(values)) == 1
    assert all(0 < value < room.capacity for value in values)


def test_occupancy_resumes_normal_scenario_after_class_ends():
    room = SimpleNamespace(
        id=102,
        code="EN-L1",
        capacity=35,
        timetable=[
            {
                "day_of_week": "Monday",
                "start_time": "11:00",
                "end_time": "12:00",
                "course_name": "Prototype Lab",
            }
        ],
    )

    at_start = current_readings([room], datetime(2026, 9, 21, 11, 0, 0))[0].occupancy
    at_end = current_readings([room], datetime(2026, 9, 21, 11, 58, 0))[0].occupancy
    after_end = current_readings([room], datetime(2026, 9, 21, 12, 2, 0))[0].occupancy

    assert at_end == at_start
    assert after_end != at_start
    assert after_end == occupancy_for(
        room.code,
        room.capacity,
        ROOM_EMPTYING,
        datetime(2026, 9, 21, 12, 2, 0),
    )