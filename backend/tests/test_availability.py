"""Tests for the Stage 3 availability engine (pure timetable -> state logic).

Every test uses a fixed datetime, so the result never depends on the machine
clock. The boundary convention under test: start time is inclusive, end time
is exclusive.
"""

from datetime import datetime

from app.services.availability import (
    AVAILABLE,
    IN_CLASS,
    WEEKDAY_NAMES,
    decide,
    find_active_slot,
)

ECON_SLOT = {
    "day_of_week": "Monday",
    "start_time": "11:30",
    "end_time": "13:00",
    "course_name": "Introduction to Economics (ECO101)",
}

MATH_SLOT = {
    "day_of_week": "Monday",
    "start_time": "08:00",
    "end_time": "09:30",
    "course_name": "Discrete Mathematics (MATH201)",
}


def monday(hour: int, minute: int = 0) -> datetime:
    """2026-09-21 is a Monday — handy fixed anchor for timetable tests."""
    return datetime(2026, 9, 21, hour, minute)


def test_weekday_table_maps_python_monday_to_monday():
    assert WEEKDAY_NAMES[monday(12).weekday()] == "Monday"


def test_room_with_no_timetable_is_available():
    decision = decide([], monday(12))

    assert decision.state == AVAILABLE
    assert decision.active_slot is None
    assert "No class" in decision.reason


def test_before_class_is_available():
    decision = decide([ECON_SLOT], monday(11, 0))

    assert decision.state == AVAILABLE
    assert decision.active_slot is None


def test_exactly_at_class_start_is_in_class():
    decision = decide([ECON_SLOT], monday(11, 30))

    assert decision.state == IN_CLASS
    assert decision.active_slot is not None
    assert decision.active_slot.course_name == ECON_SLOT["course_name"]


def test_during_class_is_in_class():
    decision = decide([ECON_SLOT], monday(12, 0))

    assert decision.state == IN_CLASS


def test_exactly_at_class_end_is_available():
    # End time is exclusive: 13:00 belongs to the next gap, not the class.
    decision = decide([ECON_SLOT], monday(13, 0))

    assert decision.state == AVAILABLE
    assert decision.active_slot is None


def test_after_class_is_available():
    decision = decide([ECON_SLOT], monday(14, 0))

    assert decision.state == AVAILABLE


def test_different_weekday_is_available():
    tuesday_noon = datetime(2026, 9, 22, 12, 0)  # a Tuesday
    assert WEEKDAY_NAMES[tuesday_noon.weekday()] == "Tuesday"

    decision = decide([ECON_SLOT], tuesday_noon)

    assert decision.state == AVAILABLE


def test_multiple_slots_select_the_correct_active_slot():
    slots = [MATH_SLOT, ECON_SLOT]

    morning = decide(slots, monday(8, 30))
    assert morning.state == IN_CLASS
    assert morning.active_slot is not None
    assert morning.active_slot.course_name == MATH_SLOT["course_name"]

    midday = decide(slots, monday(12, 0))
    assert midday.state == IN_CLASS
    assert midday.active_slot is not None
    assert midday.active_slot.course_name == ECON_SLOT["course_name"]

    between = decide(slots, monday(10, 0))
    assert between.state == AVAILABLE


def test_find_active_slot_returns_none_outside_class():
    assert find_active_slot([ECON_SLOT], monday(10, 0)) is None


def test_reasons_are_human_readable():
    free = decide([ECON_SLOT], monday(11, 0))
    assert free.reason == "No class is scheduled right now."

    busy = decide([ECON_SLOT], monday(12, 0))
    assert "Introduction to Economics (ECO101)" in busy.reason
    assert "13:00" in busy.reason
    assert "in progress" in busy.reason


def test_engine_accepts_time_objects_as_well_as_strings():
    from datetime import time

    slot = {
        "day_of_week": "Monday",
        "start_time": time(11, 30),
        "end_time": time(13, 0),
        "course_name": "Introduction to Economics (ECO101)",
    }

    assert decide([slot], monday(12, 0)).state == IN_CLASS
    assert decide([slot], monday(13, 0)).state == AVAILABLE
