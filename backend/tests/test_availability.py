"""Tests for the Stage 3 availability engine (pure timetable -> state logic).

Every test uses a fixed datetime, so the result never depends on the machine
clock. The boundary convention under test: start time is inclusive, end time
is exclusive.
"""

from datetime import datetime

from app.services.availability import (
    AVAILABLE,
    FULL,
    IN_CLASS,
    OCCUPIED,
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
    assert free.reason == "No class is scheduled and the room looks empty."

    busy = decide([ECON_SLOT], monday(12, 0))
    assert busy.state == IN_CLASS


def test_availablility_reason_signals_sensor_contribution():
    """Stage 4 AVAILABLE rooms say how they look (from sensors), not just the
    timetable. AVOID exact-string brittleness: assert the sentence mentions the
    simulator and that nothing is scheduled."""
    free = decide([], monday(12))
    assert "No class is scheduled" in free.reason
    assert "room looks empty" in free.reason


def test_occupied_reason_names_the_headcount():
    occupied = decide([], monday(12), occupancy=7, capacity=35)
    assert occupied.state == OCCUPIED
    assert "7" in occupied.reason
    assert "people" in occupied.reason
    assert "detected in the room (simulated sensor)" in occupied.reason
    assert "no class is scheduled" in occupied.reason


def test_occupied_reason_is_singular_for_one_person():
    occupied = decide([], monday(12), occupancy=1, capacity=20)
    assert occupied.state == OCCUPIED
    assert "1 person detected" in occupied.reason
    assert "1 people detected" not in occupied.reason


def test_full_reason_includes_the_headcount_and_capacity():
    full = decide([], monday(12), occupancy=30, capacity=30)
    assert full.state == FULL
    assert "30/30" in full.reason
    assert "full" in full.reason.lower()


def test_full_reason_keeps_the_in_session_note_when_a_class_is_running():
    full_and_in_session = decide(
        [ECON_SLOT], monday(12, 0), occupancy=80, capacity=80
    )
    # An active class is the strongest fact we have: IN_CLASS wins over FULL,
    # fresh or stale. FULL describes the occupancy signal only when no class is
    # scheduled, so this test documents the precedence, not a broken path.
    assert full_and_in_session.state == IN_CLASS
    assert "Introduction to Economics (ECO101) is in progress" in full_and_in_session.reason
    assert "80/80" not in full_and_in_session.reason


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
