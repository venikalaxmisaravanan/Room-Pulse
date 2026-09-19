"""Tests for current usable-room search."""

from app.schemas.availability import AvailabilityListResponse
from app.services.availability_service import find_usable_rooms


AT = "2026-09-21T12:00:00"


def find(client, **params):
    response = client.get("/api/rooms/find", params={"at": AT, **params})
    assert response.status_code == 200
    return response.json()


def test_building_filter_returns_only_currently_usable_rooms(client):
    payload = find(client, building="Science Block")
    assert all(room["building"] == "Science Block" for room in payload["rooms"])
    assert all(room["state"] in {"AVAILABLE", "OCCUPIED"} for room in payload["rooms"])


def test_room_type_and_capacity_filters_are_combined(client):
    payload = find(
        client,
        building="Science Block",
        room_type="Classroom",
        min_capacity=40,
    )
    assert all(
        room["building"] == "Science Block"
        and room["room_type"] == "Classroom"
        and room["capacity"] >= 40
        and room["state"] in {"AVAILABLE", "OCCUPIED"}
        for room in payload["rooms"]
    )
    assert payload["count"] == len(payload["rooms"])


def test_full_occupied_in_class_and_unknown_rooms_are_not_usable(client):
    payload = find(client)
    codes = {room["code"] for room in payload["rooms"]}
    assert "BS-104" not in codes  # IN_CLASS at the fixed moment
    assert all(room["state"] in {"AVAILABLE", "OCCUPIED"} for room in payload["rooms"])

    stale = find(
        client,
        building="Business Block",
        room_type="Seminar Room",
        at="2026-09-21T12:06:00",
    )
    assert "BS-301" not in {room["code"] for room in stale["rooms"]}


def test_no_match_is_a_clean_empty_snapshot(client):
    payload = find(client, building="Science Block", min_capacity=1000)
    assert payload["count"] == 0
    assert payload["rooms"] == []
    assert payload["evaluated_at"].startswith("2026-09-21T12:00:00")


def test_find_results_keep_stage_7_explanation_fields(client):
    payload = find(client)
    for room in payload["rooms"]:
        assert room["reason_code"] == room["state"]
        assert room["sensor_freshness"] is not None
        assert room["occupancy"] is not None
        assert room["usability_reason"]


def test_seats_needed_uses_remaining_capacity_and_preserves_blocking_states(client):
    snapshot = AvailabilityListResponse.model_validate(
        client.get("/api/rooms/availability", params={"at": AT}).json()
    )
    base = snapshot.rooms[0]

    def room(code, state, capacity, occupancy, fresh=True):
        return base.model_copy(
            update={
                "code": code,
                "state": state,
                "reason_code": state,
                "capacity": capacity,
                "occupancy": base.occupancy.model_copy(
                    update={
                        "capacity": capacity,
                        "occupancy": occupancy,
                        "remaining_capacity": capacity - occupancy,
                    }
                ),
                "sensor_freshness": base.sensor_freshness.model_copy(
                    update={"fresh": fresh, "status": "FRESH" if fresh else "STALE"}
                ),
            }
        )

    controlled = snapshot.model_copy(
        update={
            "rooms": [
                room("EMPTY", "AVAILABLE", 50, 0),
                room("PARTIAL", "OCCUPIED", 126, 40),
                room("TOO-SMALL", "OCCUPIED", 50, 45),
                room("FULL", "FULL", 50, 50),
                room("STALE", "UNKNOWN", 126, 40, fresh=False),
                room("MISSING", "UNKNOWN", 126, 40),
                room("CLASS", "IN_CLASS", 126, 40),
            ]
        }
    )
    controlled.rooms[4].sensor_freshness = None

    result = find_usable_rooms(controlled, seats_needed=10)

    assert [room.code for room in result.rooms] == ["EMPTY", "PARTIAL"]
    partial = result.rooms[1]
    assert partial.state == "OCCUPIED"
    assert partial.occupancy.remaining_capacity == 86
    assert partial.usability_reason == "86 seats currently available."


def test_filter_combination_and_ordering_on_a_current_snapshot(client):
    snapshot = AvailabilityListResponse.model_validate(
        client.get("/api/rooms/availability", params={"at": AT}).json()
    )
    first = snapshot.rooms[0].model_copy(
        update={
            "state": "AVAILABLE",
            "reason_code": "AVAILABLE",
            "building": "Science Block",
            "room_type": "Classroom",
            "capacity": 50,
        }
    )
    second = snapshot.rooms[1].model_copy(
        update={
            "state": "AVAILABLE",
            "reason_code": "AVAILABLE",
            "building": "Science Block",
            "room_type": "Classroom",
            "capacity": 40,
        }
    )
    full = snapshot.rooms[2].model_copy(update={"state": "FULL"})
    unknown = snapshot.rooms[3].model_copy(update={"state": "UNKNOWN"})
    in_class = snapshot.rooms[4].model_copy(update={"state": "IN_CLASS"})
    occupied = snapshot.rooms[5].model_copy(update={"state": "OCCUPIED"})
    controlled = snapshot.model_copy(
        update={"rooms": [first, second, full, unknown, in_class, occupied]}
    )

    result = find_usable_rooms(
        controlled,
        building="Science Block",
        room_type="Classroom",
        min_capacity=45,
        seats_needed=10,
    )
    assert [room.code for room in result.rooms] == [first.code]
    assert result.count == 1
    assert all(room.state == "AVAILABLE" for room in result.rooms)
