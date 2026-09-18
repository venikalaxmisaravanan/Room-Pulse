"""Tests for the availability API (`GET /api/rooms/availability`).

The endpoint is read-only and derived: it loads the seeded catalogue, runs
the engine at one moment and returns the answer. Nothing is stored.
"""

from app.db.seed_data import ROOMS

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
    "timetable",
}

# A Monday midday moment where the seed data has both kinds of rooms:
# EN-101 (Mon 08:00-09:30 only) is free, BS-104 (Mon 11:30-13:00) is busy.
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

    free = rooms["EN-101"]
    assert free["state"] == "AVAILABLE"
    assert free["active_class"] is None
    assert free["reason"] == "No class is scheduled right now."


def test_availability_summary_counts_match_the_room_states(client):
    payload = client.get(
        "/api/rooms/availability", params={"at": MONDAY_MIDDAY}
    ).json()

    states = [room["state"] for room in payload["rooms"]]
    assert payload["available_count"] == states.count("AVAILABLE")
    assert payload["in_class_count"] == states.count("IN_CLASS")
    assert payload["available_count"] + payload["in_class_count"] == payload["count"]
    # This fixture moment really does produce a mix of both states.
    assert payload["available_count"] > 0
    assert payload["in_class_count"] > 0


def test_availability_reports_the_evaluated_moment(client):
    payload = client.get(
        "/api/rooms/availability", params={"at": MONDAY_MIDDAY}
    ).json()

    assert payload["evaluated_at"].startswith("2026-09-21T12:00:00")


def test_availability_rejects_an_invalid_datetime(client):
    response = client.get("/api/rooms/availability", params={"at": "not-a-date"})

    assert response.status_code == 400


def test_rooms_endpoint_still_returns_the_plain_catalogue(client):
    response = client.get("/api/rooms")

    assert response.status_code == 200
    assert response.json()["count"] == len(ROOMS)


def test_api_still_exposes_no_write_routes(client):
    schema = client.get("/openapi.json").json()

    assert set(schema["paths"]) == {
        "/api/health",
        "/api/rooms",
        "/api/rooms/availability",
    }
    assert set(schema["paths"]["/api/rooms/availability"]) == {"get"}
    assert set(schema["paths"]["/api/rooms"]) == {"get"}
