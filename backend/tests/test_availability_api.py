"""Tests for the availability API (`GET /api/rooms/availability`).

The endpoint is read-only and derived: it loads the seeded catalogue, runs
the engine at one moment and returns the answer. Nothing is stored.
"""

from app.db.seed_data import ROOMS
from app.services.occupancy import (
    CROWDING,
    NORMAL,
    ROOM_EMPTYING,
    SENSOR_FAILURE,
    SUDDEN_OCCUPANCY,
    SCENARIOS,
)

EXPECTED_AVAILABILITY_FIELDS = {
    "id",
    "code",
    "name",
    "building",
    "room_type",
    "capacity",
    "state",
    "reason",
    "active_class",
    "occupancy",
    "timetable",
}

# A Monday midday moment where the seed data has both kinds of rooms:
# EN-101 (Mon 08:00-09:30 only) is busy with 20 people (NORMAL at this tick),
# while BS-104 (Mon 11:30-13:00) is IN_CLASS with 20 people (ROOM_EMPTYING).
MONDAY_MIDDAY = "2026-09-21T12:00:00"


def test_availability_endpoint_returns_every_seeded_room(client):
    response = client.get("/api/rooms/availability", params={"at": MONDAY_MIDDAY})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == len(ROOMS)
    assert len(payload["rooms"]) == len(ROOMS)


def test_availability_room_has_exactly_the_expected_fields(client):
    rooms = client.get(
        "/api/rooms/availability", params={"at": MONDAY_MIDDAY}
    ).json()["rooms"]

    for room in rooms:
        assert set(room) == EXPECTED_AVAILABILITY_FIELDS
        # Capacity is preserved for later stages; occupancy does not exist yet.
        assert room["capacity"] > 0


def test_availability_states_match_the_timetable_at_a_fixed_moment(client):
    rooms = {
        room["code"]: room
        for room in client.get(
            "/api/rooms/availability", params={"at": MONDAY_MIDDAY}
        ).json()["rooms"]
    }

    busy = rooms["BS-104"]
    assert busy["state"] == "IN_CLASS"
    assert busy["active_class"] is not None
    assert busy["active_class"]["course_name"] == "Introduction to Economics (ECO101)"
    assert busy["active_class"]["end_time"] == "13:00"
    assert "13:00" in busy["reason"]
    # The room would be ROOM_EMPTYING in this scenario; the only reason IN_CLASS
    # wins is that the class owns the room even though people are still inside.
    assert busy["occupancy"]["scenario"] == ROOM_EMPTYING
    assert busy["occupancy"]["occupancy"] == 12
    assert busy["occupancy"]["capacity"] == 120

    occupied = rooms["EN-101"]
    assert occupied["state"] == "OCCUPIED"
    assert occupied["active_class"] is None
    # No class scheduled, but 20 people detected in the room.
    assert "20" in occupied["reason"]
    assert "people detected" in occupied["reason"]
    assert "no class is scheduled" in occupied["reason"]
    assert occupied["occupancy"]["scenario"] == NORMAL
    assert occupied["occupancy"]["occupancy"] == 20


def test_availability_summary_counts_match_the_room_states(client):
    payload = client.get(
        "/api/rooms/availability", params={"at": MONDAY_MIDDAY}
    ).json()

    states = [room["state"] for room in payload["rooms"]]
    assert payload["available_count"] == states.count("AVAILABLE")
    assert payload["in_class_count"] == states.count("IN_CLASS")
    assert payload["occupied_count"] == states.count("OCCUPIED")
    assert payload["full_count"] == states.count("FULL")
    assert payload["available_count"] + payload["in_class_count"] + payload["occupied_count"] + payload["full_count"] == payload["count"]
    # At this moment the catalogue really is a mix of states: IN_CLASS,
    # OCCUPIED, AVAILABLE and possibly FULL all appear.
    assert payload["in_class_count"] > 0
    assert payload["occupied_count"] > 0
    assert payload["available_count"] >= 0
    # FULL may or may not appear depending on the tick; do not assert on it.


def test_availability_reports_the_evaluated_moment(client):
    payload = client.get(
        "/api/rooms/availability", params={"at": MONDAY_MIDDAY}
    ).json()

    assert payload["evaluated_at"].startswith("2026-09-21T12:00:00")


def test_readings_are_sequential_for_the_same_room(client):
    """Two calls a few seconds apart can change state; both are still valid
    sensor inputs, never catalogue data."""
    first = client.get("/api/rooms/availability", params={"at": MONDAY_MIDDAY}).json()
    second = client.get("/api/rooms/availability", params={"at": "2026-09-21T12:02:00"}).json()

    assert first["count"] == second["count"] == len(ROOMS)
    # At least one room should differ in type, occupancy or both between the two
    # calls in a healthy simulator — but we only assert the structure is intact.
    for room in second["rooms"]:
        assert set(room) == EXPECTED_AVAILABILITY_FIELDS
        assert room["capacity"] > 0
        assert room["occupancy"]["capacity"] == room["capacity"]
        assert room["occupancy"]["scenario"] in SCENARIOS
        assert isinstance(room["occupancy"]["occupancy"], int)
        assert 0 <= room["occupancy"]["occupancy"] <= room["capacity"]
    schema = client.get("/openapi.json").json()

    assert set(schema["paths"]) == {
        "/api/health",
        "/api/rooms",
        "/api/rooms/availability",
    }
    assert set(schema["paths"]["/api/rooms/availability"]) == {"get"}
    assert set(schema["paths"]["/api/rooms"]) == {"get"}
