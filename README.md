# RoomPulse

> Find a room you can actually use right now.

## Overview

RoomPulse is a prototype campus room-availability engine that combines timetable information, simulated occupancy sensor readings, sensor freshness, room capacity, and deterministic room-state rules. The project answers a student-facing question: which room can actually be used right now, not just which room is free on paper.

Availability is computed at read time rather than stored in the database. The catalogue holds room metadata and timetable data, while the backend evaluates the current state from the latest inputs. The result is a single room snapshot, explained in plain language, which the dashboard can display and a student can filter for usable capacity.

The final project includes:

- a FastAPI backend
- a SQLite + SQLAlchemy catalogue
- a deterministic timetable availability engine
- a simulated occupancy model
- stale-data and freshness checks
- real-time WebSocket updates
- a Find Me a Room search based on trusted remaining capacity

## Problem

Students do not just need to know whether a timetable says a room is free. They need to know whether they can actually use the room right now for the number of people in their group. A timetable may say a room is not scheduled, but it may still be full, partly occupied, or missing trustworthy sensor data.

RoomPulse addresses that gap by separating room state from student usability.

## Core concept

The core logic is:

Timetable + simulated occupancy + capacity + sensor freshness
→ availability engine
→ room state
→ student usability
→ real-time dashboard

This distinction matters:

- Room state answers: What is happening in the room right now?
- Student usability answers: Can this student or group use the room for the requested number of seats?

Example:

- Capacity: 120
- Occupancy: 54
- Remaining: 66
- State: OCCUPIED

If a student requests 10 seats, then 66 >= 10, so the room can be returned by Find Me a Room. The UI still shows OCCUPIED because that is the room state, even when the room is usable for additional students.

## Room states

The implemented room states are:

### AVAILABLE
No class is scheduled and the room has no trusted occupancy.

### OCCUPIED
People are inside and no class is scheduled. Remaining seats may still be available.

### IN_CLASS
A scheduled class is currently in progress.

### FULL
Trusted occupancy has reached the room capacity.

### UNKNOWN
Sensor data is stale or unavailable, so RoomPulse cannot safely determine usability.

The room state and the student search are intentionally separate. A room can be OCCUPIED without being unusable for a smaller group, while IN_CLASS, FULL and UNKNOWN remain excluded from student usability.

## Student usability / Find Me a Room

Find Me a Room searches the latest snapshot for rooms that can accommodate the requested number of students. It does not run a second availability engine; it applies a capacity-aware usability filter to the current snapshot.

The implemented search uses:

- building filter
- room type filter
- minimum room capacity
- seats needed
- remaining capacity
- trusted fresh sensor data

A room is considered usable only when:

- its state is AVAILABLE or OCCUPIED
- sensor freshness is trusted
- remaining capacity is at least the requested number of seats
- the room is not FULL
- the room is not IN_CLASS
- the room is not UNKNOWN

This means a partially occupied room can still be returned when enough seats remain for the group. The state badge remains OCCUPIED, but the room may still be usable.

## Architecture

### Frontend
React + Vite

### Backend
Python + FastAPI

### Database
SQLite + SQLAlchemy

### Simulation
Python occupancy simulator

### Real-time
WebSocket live updates

### Testing
pytest

Architecture flow:

```text
Seeded room catalogue (SQLite)
        ↓
Timetable + occupancy + freshness evaluation
        ↓
Derived room state + explanation
        ↓
Student usability filter for Find Me a Room
        ↓
React dashboard + live WebSocket updates
```

## Project structure

```text
RoomPulse/
├── README.md
├── backend/
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── roompulse.db
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── availability.py
│       │       ├── find.py
│       │       ├── health.py
│       │       ├── occupancy.py
│       │       ├── rooms.py
│       │       └── ws.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── database.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── init_db.py
│       │   └── seed_data.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── room.py
│       │   └── timetable.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── availability.py
│       │   ├── health.py
│       │   ├── occupancy.py
│       │   └── room.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── availability.py
│       │   ├── availability_service.py
│       │   ├── occupancy.py
│       │   ├── room_service.py
│       │   ├── sensor_freshness.py
│       │   └── wslive.py
│       └── tests/
│           ├── conftest.py
│           ├── test_availability.py
│           ├── test_availability_api.py
│           ├── test_find_rooms_api.py
│           ├── test_models.py
│           ├── test_rooms_api.py
│           └── test_ws.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── api/
│       │   └── client.js
│       ├── components/
│       │   ├── FiltersBar.jsx
│       │   ├── HeaderBar.jsx
│       │   ├── RoomCard.jsx
│       │   ├── RoomResults.jsx
│       │   ├── StatusLegend.jsx
│       │   └── SummaryCards.jsx
│       ├── constants/
│       │   └── roomStates.js
│       ├── hooks/
│       │   ├── useAvailability.js
│       │   ├── useBackendHealth.js
│       │   └── useRooms.js
│       └── utils/
│           └── roomFilters.js
└── .gitignore
```

## API endpoints

The backend is mounted under `/api`.

### GET /api/health
Returns service health and environment metadata. This is used by the frontend to check whether the backend can respond.

### GET /api/rooms
Returns the room catalogue and timetable data from SQLite. No availability, occupancy, or current status is stored here.

### GET /api/rooms/availability
Returns one derived room-state snapshot for the current time. Each room includes:

- state
- reason
- active class when relevant
- occupancy data
- sensor freshness flags
- room catalogue details

Optional query parameter:

- `at` — ISO datetime used to evaluate a fixed moment instead of the current system time.

### GET /api/rooms/occupancy
Returns the current simulated occupancy readings for each room. The readings are transient in-memory data; they are not stored in SQLite.

### GET /api/rooms/find
Returns rooms that are currently usable for the requested group size, using the latest availability snapshot and the filters below.

Optional query parameters:

- `building` — exact building name filter
- `room_type` — exact room type filter
- `min_capacity` — minimum capacity requirement
- `seats_needed` — required number of seats still available
- `at` — ISO datetime used for a fixed evaluation moment

### WebSocket /api/ws
Lives at `/api/ws` and streams live snapshots to connected browsers without a page refresh. The frontend connects to this endpoint and updates the dashboard as room states change in the simulator loop.

## Availability engine

The final engine is in `backend/app/services/availability.py` and combines the same inputs the product uses in the UI:

- timetable slots
- current moment
- room capacity
- simulated occupancy reading
- sensor freshness verdict

Determination order is explicit and deterministic:

1. If a timetable slot is active, the room is `IN_CLASS`.
2. If no class is active and the occupancy signal is trusted and at capacity, the room is `FULL`.
3. If no class is active and the occupancy signal is trusted and positive, the room is `OCCUPIED`.
4. If no class is active and the occupancy signal cannot be trusted, the room is `UNKNOWN`.
5. Otherwise, the room is `AVAILABLE`.

This means the engine is not just “class in session or not”; it is a combined classification of room state based on timetable, occupancy, capacity and freshness.

## Sensor freshness

Sensor freshness is implemented in `backend/app/services/sensor_freshness.py`. The prototype does not connect to real physical sensors; it uses simulated sensor readings. A reading can be:

- fresh and trusted
- stale and untrusted
- absent and untrusted

A stale or missing reading blocks the system from confidently claiming a room is usable. This prevents the UI from treating a room as safe-to-use when the data is not dependable.

## Real-time WebSocket

The WebSocket endpoint is implemented in `backend/app/api/routes/ws.py`. It connects to a shared live loop that:

1. advances the simulator by one tick,
2. evaluates the catalogue against the simulator’s current time,
3. pushes the full derived snapshot to each connected browser,
4. keeps the connection alive with a heartbeat pattern.

The dashboard uses the same room-state payload as the REST availability endpoint, so there is no separate real-time schema to maintain.

## Explainable status

Each room includes the fields the frontend actually uses to explain the status, including:

- state
- occupancy
- capacity
- remaining seats where available
- sensor freshness
- reason
- active class when applicable

The frontend therefore shows the current status and a human-readable explanation, not just a colour badge.

## Testing

The current pytest suite exercises the implemented behaviour across the project:

- models
- availability rules
- API endpoints
- occupancy simulation
- sensor freshness
- Find Me a Room search
- WebSocket contract

The suite is designed to validate the current prototype behaviour rather than older stage-only assumptions.

## Setup and running

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend at http://localhost:5173 and confirm the backend at http://127.0.0.1:8000/api/health.

## Manual demo flow

1. Start the backend.
2. Start the frontend.
3. Open the dashboard.
4. Observe the WebSocket connection status and live updates.
5. Inspect room states and simulated occupancy values.
6. Check the sensor freshness details.
7. Enter a number in Seats needed in Find Me a Room.
8. Show that a partially occupied room can still be returned when enough seats remain.
9. Show that FULL, UNKNOWN and IN_CLASS rooms are excluded.
10. Explain that the room state remains OCCUPIED even when the room is still usable for additional students.

This is the key demonstration for presentations and demos.

## Limitations / prototype scope

This project is intentionally a prototype.

- Occupancy is simulated rather than coming from real physical sensors.
- Timetable data is prototype seed data.
- There is no real authentication layer.
- There is no actual reservation management system.
- No CCTV or computer-vision system is implemented.
- No production deployment is implied.
- SQLite is appropriate for the prototype and local development workflow.

These are boundaries of the current implementation, not failures.

## Future scope

Possible future work includes:

- real occupancy sensor integration
- actual faculty reservation integration
- post-class observation windows
- authenticated student and faculty workflows
- production database and deployment
- richer campus integration

## AI usage / development disclosure

AI tools were used during the development of this project for implementation assistance, debugging, test generation, code inspection, architecture review and documentation support. The project was developed iteratively and the final code was reviewed and tested by the developer.

## Credits

This project uses:

- FastAPI
- SQLAlchemy
- SQLite
- React
- Vite
- pytest
- Starlette WebSockets

The prototype uses these libraries to deliver a local, explainable room-status prototype without claiming production-scale campus integration.

## Development stages

The final project progressed through the following stages:

### Stage 1 — foundation
Set up the project structure, backend health endpoint, basic React shell and the initial dashboard foundation.

### Stage 2 — room catalogue + timetable
Added the SQLite catalogue and timetable data model, plus seeded room data and read-only room listing endpoints.

### Stage 3 — timetable availability engine
Introduced the deterministic room-state engine based on timetable and current moment, with readable reasons for each state.

### Stage 4 — occupancy simulation
Added simulated occupancy readings and capacity-aware room-state context.

### Stage 5 — sensor freshness
Added freshness checks so stale or missing signals do not incorrectly claim a room is usable.

### Stage 6 — real-time WebSocket updates
Streamed room snapshots to the browser so the dashboard updates without a page refresh.

### Stage 7 — explainable room status
Brought in human-readable reasons, active-class details and more transparent room-state explanations.

### Stage 8 — Find Me a Room
Added the student-focused room search that filters the latest live snapshot by building, room type, minimum capacity and required seats.

### Stage 9 — capacity-aware student usability
Separated room state from student usefulness so partially occupied rooms can be returned when they still have enough remaining seats.

## Important README rules

- The README describes the final current project, not a stage-only prototype.
- It does not claim reservations are implemented.
- It does not claim real physical sensors are connected.
- It does not describe WebSocket or Find Me a Room as future ideas.
- It clearly differentiates room state from student usability.
- It keeps prototype boundaries honest without treating them as failures.
