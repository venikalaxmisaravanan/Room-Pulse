"""Tests for the room catalogue API (`GET /api/rooms`)."""

from app.db.seed_data import ROOMS
from app.models import WEEKDAYS

EXPECTED_ROOM_FIELDS = {
    "id",
    "code",
    "name",
    "building",
    "room_type",
    "capacity",
    "timetable",
}

# Words that must never appear in a room payload in this stage: availability is
# derived later, so the API must not pretend to know it.
FORBIDDEN_FIELDS = {
    "available",
    "availability",
    "current_status",
    "status",
    "occupied",
    "is_free",
    "reserved",
}


def test_health_endpoint_still_works(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rooms_endpoint_returns_the_seeded_catalogue(client):
    response = client.get("/api/rooms")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == len(ROOMS)
    assert len(payload["rooms"]) == len(ROOMS)


def test_room_payload_has_exactly_the_expected_fields(client):
    rooms = client.get("/api/rooms").json()["rooms"]

    for room in rooms:
        assert set(room) == EXPECTED_ROOM_FIELDS


def test_room_payload_contains_no_availability_information(client):
    payload = client.get("/api/rooms").json()

    assert FORBIDDEN_FIELDS.isdisjoint(payload["rooms"][0])
    # Guard against a status sneaking in through the nested timetable objects.
    for room in payload["rooms"]:
        for slot in room["timetable"]:
            assert FORBIDDEN_FIELDS.isdisjoint(slot)


def test_rooms_are_ordered_by_code_with_unique_codes(client):
    rooms = client.get("/api/rooms").json()["rooms"]

    codes = [room["code"] for room in rooms]
    assert codes == sorted(codes)
    assert len(codes) == len(set(codes))


def test_room_facts_match_the_seed_data(client):
    rooms = {room["code"]: room for room in client.get("/api/rooms").json()["rooms"]}

    for entry in ROOMS:
        room = rooms[entry["code"]]
        assert room["name"] == entry["name"]
        assert room["building"] == entry["building"]
        assert room["room_type"] == entry["room_type"]
        assert room["capacity"] == entry["capacity"]


def test_timetable_slots_belong_to_the_correct_room(client):
    rooms = {room["code"]: room for room in client.get("/api/rooms").json()["rooms"]}
    expected_courses = {
        slot["course_name"] for slot in ROOMS[0]["timetable"]
    }

    en_101 = rooms["EN-101"]
    assert {slot["course_name"] for slot in en_101["timetable"]} == expected_courses

    # A different room must not have picked up those slots.
    assert "Discrete Mathematics (MATH201)" not in {
        slot["course_name"] for slot in rooms["SC-L2"]["timetable"]
    }


def test_every_timetable_slot_is_valid_and_sorted(client):
    for room in client.get("/api/rooms").json()["rooms"]:
        slots = room["timetable"]
        assert slots, f"{room['code']} should have prototype timetable slots"

        sort_keys = [
            (WEEKDAYS.index(slot["day_of_week"]), slot["start_time"])
            for slot in slots
        ]
        assert sort_keys == sorted(sort_keys), f"{room['code']} slots are unsorted"

        for slot in slots:
            assert slot["day_of_week"] in WEEKDAYS
            assert slot["start_time"] < slot["end_time"]
            assert slot["course_name"]


def test_api_exposes_no_write_routes(client):
    schema = client.get("/openapi.json").json()

    assert set(schema["paths"]) == {
        "/api/health",
        "/api/rooms",
        "/api/rooms/availability",
        "/api/rooms/find",
        "/api/rooms/occupancy",
    }
    assert set(schema["paths"]["/api/health"]) == {"get"}
    assert set(schema["paths"]["/api/rooms"]) == {"get"}
    assert set(schema["paths"]["/api/rooms/availability"]) == {"get"}
    assert set(schema["paths"]["/api/rooms/find"]) == {"get"}
    assert set(schema["paths"]["/api/rooms/occupancy"]) == {"get"}