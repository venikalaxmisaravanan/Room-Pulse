# RoomPulse — Real-Time Campus Room Availability Engine

## Problem statement

Campus rooms are shared between classes, group work, faculty bookings and
whatever is happening in them at that exact moment. A timetable tells you when a
class is *supposed* to be there, a booking sheet tells you who *asked* for a room,
and a sensor tells you who is *actually* inside — but a student standing in a
corridor usually has none of that, and ends up walking from door to door.
RoomPulse answers a single question: **"Which campus room can I actually use right
now?"**

## Core idea

Room availability is **derived, not stored**. There is no `available` column
anywhere in this project — not in the API, not in the SQLite schema. Instead,
every room has several changing inputs, and one deterministic availability engine
will turn them into one current state:

```
Timetable + Occupancy + Reservations + Capacity + Sensor Freshness
        │
        ▼
Availability Engine  (precedence rules, conflict handling)
        │
        ▼
Current Room State: AVAILABLE · OCCUPIED · IN_CLASS · RESERVED · FULL · UNKNOWN
        │
        ▼
Real-time student dashboard (with an explanation for every state)
```

Because the state is computed from sources, the dashboard can also *explain
itself* ("in class until 11:30, sensor stale for 9 minutes"), and stale or
conflicting data becomes `UNKNOWN` instead of a confidently wrong answer.

**Today the engine does not exist**, so the dashboard deliberately shows
`UNKNOWN` for every room. That is a statement about the system, not a placeholder
for missing data: the timetable is real, but nothing turns it into "can I use
this room right now?" yet.

## Planned architecture

| Layer | Choice | Status |
| --- | --- | --- |
| Frontend | React (Vite, plain JavaScript) | Stage 2 — dashboard reads real rooms |
| Backend | Python + FastAPI | Stage 2 — `/api/health`, `/api/rooms` |
| Database | SQLite + SQLAlchemy | Stage 2 — rooms + timetable slots |
| Simulation | Python | Later — occupancy simulator emitting sensor readings |
| Real-time | WebSocket | Later — pushes room states to the dashboard |

```
RoomPulse/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, CORS, /api router mounting
│   │   ├── core/              config.py (paths, env) + database.py (engine, Base, get_db)
│   │   ├── api/routes/        health.py, rooms.py  (one file per concern)
│   │   ├── models/            room.py, timetable.py  (SQLAlchemy tables)
│   │   ├── schemas/           health.py, room.py  (pydantic response shapes)
│   │   ├── services/          room_service.py  (read-only reads + sorting)
│   │   └── db/                seed_data.py (hand-written data), init_db.py (create + seed)
│   ├── tests/                 pytest tests for the models and the API
│   └── requirements.txt       fastapi, uvicorn, SQLAlchemy  (+ requirements-dev.txt: pytest, httpx)
└── frontend/
    └── src/
        ├── api/client.js          one place for every backend call
        ├── hooks/                 useBackendHealth.js, useRooms.js
        ├── utils/roomFilters.js   pure filtering helpers
        ├── constants/             roomStates.js (the six future states)
        └── components/            HeaderBar, FiltersBar, SummaryCards, RoomResults, RoomCard, StatusLegend
```

## Data model

Two tables, created from the models on startup. Nothing about availability is
stored, because availability is an opinion about the current moment, not a
property of a room.

**`rooms`**

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | integer (PK) | Internal identifier |
| `code` | text (unique) | The code on the door, e.g. `EN-101` |
| `name` | text | Human-friendly name, e.g. "Lecture Hall EN-101" |
| `building` | text | e.g. `Engineering Block` |
| `room_type` | text | Classroom / Computer Laboratory / Electronics Laboratory / Seminar Room |
| `capacity` | integer | Seats |

**`timetable_slots`**

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | integer (PK) | Internal identifier |
| `room_id` | integer (FK → `rooms.id`) | Which room the session is in |
| `day_of_week` | text | `Monday` … `Saturday` (matches `date.strftime("%A")`) |
| `start_time` / `end_time` | time | Session window |
| `course_name` | text | e.g. "Databases Lab (CS210L)" |

`Room.timetable` ↔ `TimetableSlot.room` is a one-to-many relationship, so the
API can nest each room's slots inside the room it belongs to.

Deliberately **absent** from both tables: `available`, `current_status`,
`occupied`, `is_free`, `reserved`. A test asserts those columns do not exist, so
the rule cannot be broken by accident.

## Prototype seed data

`backend/app/db/seed_data.py` holds a small, **hand-written and deterministic**
dataset: no randomness, no generated bulk rows. Seeding the same file twice
produces the same database.

**9 rooms across 3 buildings** (20–120 seats, 4 room types):

| Code | Name | Building | Type | Capacity | Slots |
| --- | --- | --- | --- | --- | --- |
| EN-101 | Lecture Hall EN-101 | Engineering Block | Classroom | 80 | 3 |
| EN-102 | Tutorial Room EN-102 | Engineering Block | Classroom | 40 | 3 |
| EN-L1 | Computer Laboratory L1 | Engineering Block | Computer Laboratory | 35 | 4 |
| SC-115 | Lecture Hall SC-115 | Science Block | Classroom | 90 | 3 |
| SC-210 | Seminar Room SC-210 | Science Block | Seminar Room | 25 | 3 |
| SC-L2 | Electronics Laboratory L2 | Science Block | Electronics Laboratory | 30 | 3 |
| BS-104 | Lecture Hall BS-104 | Business Block | Classroom | 120 | 3 |
| BS-301 | Case Study Room BS-301 | Business Block | Seminar Room | 20 | 4 |
| BS-L3 | Computer Laboratory L3 | Business Block | Computer Laboratory | 45 | 3 |

**29 timetable slots** across Monday–Saturday, using realistic session windows
(08:00–09:30, 09:45–11:15, 11:30–13:00, 14:00–15:30, 15:45–17:15, plus one
Saturday workshop and one 18:00 evening seminar).

The gaps are intentional, so later stages have something real to demonstrate:

- Rooms that stay free on a whole day (EN-101 and BS-104 have nothing on
  Tuesday or Thursday) → room for `AVAILABLE` next to `IN_CLASS`.
- Several rooms in class at the same time in different buildings → timetable vs
  occupancy vs reservation conflicts.
- Sessions outside normal hours (Saturday workshop, evening seminar) → a
  timetable that disagrees with a stale sensor.

Nothing in the seed data decides availability.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Is the backend running? (service, version, environment, timestamp) |
| GET | `/api/rooms` | The room catalogue from SQLite, timetable slots nested per room |
| GET | `/` | Signpost with links to `/docs`, `/api/health`, `/api/rooms` (not part of the schema) |

There are **no write endpoints**. The catalogue is seeded from a file so it stays
deterministic; a test asserts that `/api/rooms` only exposes `GET`.

`GET /api/rooms` response (trimmed):

```json
{
  "count": 9,
  "rooms": [
    {
      "id": 7,
      "code": "BS-104",
      "name": "Lecture Hall BS-104",
      "building": "Business Block",
      "room_type": "Classroom",
      "capacity": 120,
      "timetable": [
        {
          "id": 20,
          "day_of_week": "Monday",
          "start_time": "11:30:00",
          "end_time": "13:00:00",
          "course_name": "Introduction to Economics (ECO101)"
        }
      ]
    }
  ]
}
```

Timetable slots are nested per room (no joining in the frontend) and sorted
Monday-first, then by start time. There is **no status/availability field** in
the payload — the API only reports what it actually knows.

## Dashboard behaviour

- **Room cards** show the code, name, building, type, capacity and the prototype
  timetable (first three sessions, then "+n more").
- **Every card shows the `UNKNOWN` badge**, plus a notice above the grid
  explaining that `UNKNOWN` is intentional until the availability engine exists.
- **Summary cards** (Available / Occupied / Reserved) still show `—`. Counting
  rooms would require the engine; printing `0` would be a claim RoomPulse cannot
  back up.
- **Filters work**: building, room type and minimum capacity filter the loaded
  catalogue in the browser (9 rooms, so no extra endpoint is needed). They are
  disabled until the catalogue arrives, and a "Clear filters" button appears once
  something is set.
- **States that are handled**: loading, request failure (with the reason and a
  "Try again" button), empty catalogue, and "no rooms match your filters". No
  invented rooms are ever shown.

## MVP feature list

Must-have:

1. Multi-source availability engine — *not implemented*
2. Deterministic conflict / precedence rules — *not implemented*
3. Dynamic occupancy simulator — *not implemented*
4. Sensor freshness / stale-data detection — *not implemented*
5. Real-time dashboard — *partly: initial fetch only, no WebSocket yet*
6. Explainable room status — *not implemented*
7. Capacity-aware availability — *not implemented (capacity is displayed and filterable)*
8. "Find Me a Room" filtering / query — *partly: catalogue filters only, not availability-aware*

If time permits later:

9. Post-class observation window — *not implemented*
10. Faculty reservation with interval-conflict checking — *not implemented*
11. Concurrency-safe room claims — *not implemented*

## Current implementation status

### Stage 1 — project foundation + UI shell (done)

- FastAPI backend with `GET /api/health`.
- React + Vite dashboard shell: branding, tagline, header status indicator wired
  to the real health endpoint, filter placeholders, summary cards, empty room
  section, room-state legend.
- Vite dev proxy so the frontend calls `/api/...` on its own origin.

### Stage 2 — room catalogue + timetable from SQLite (done)

- SQLite database created and seeded automatically on startup
  (`backend/roompulse.db`, git-ignored).
- SQLAlchemy models `Room` and `TimetableSlot`, connected one-to-many, with **no
  stored availability field**.
- Hand-written, deterministic prototype data: 9 rooms, 3 buildings, 29 slots.
- Read-only `GET /api/rooms` returning rooms with nested timetable slots.
- Dashboard renders real room cards from the API, each marked `UNKNOWN`, with
  working building / type / capacity filters and honest loading, error and empty
  states.
- Backend tests for the models, the seed data and the API (16 tests).

### Not implemented yet

- The availability engine and all room-state logic (the six states exist only as
  legend text).
- Occupancy simulation, sensor freshness, capacity-aware availability logic.
- Reservations, concurrency-safe claims, post-class observation window.
- Real-time WebSocket updates (the dashboard fetches once on load).
- Explainable status ("in class until 11:30 …").
- Authentication, student/faculty accounts, CCTV/computer vision, notifications,
  chatbot, mobile app — out of scope for this project.

## Local setup and run instructions

Two terminals. Backend first, then frontend.

### 1. Backend (FastAPI + SQLite)

Requires Python 3.9+ (developed on 3.11).

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The database is prepared automatically on startup: the tables are created from
the models and the prototype data is inserted **only if the room table is empty**,
so restarting the server never duplicates or resets anything.

You can also do it explicitly (and rebuild from scratch):

```powershell
python -m app.db.init_db            # create tables, seed if empty
python -m app.db.init_db --reset    # drop everything and seed again
```

The database file is `backend/roompulse.db` (ignored by Git).

Verify the backend:

- Health check: <http://127.0.0.1:8000/api/health>
- Room catalogue: <http://127.0.0.1:8000/api/rooms>
- Interactive API docs: <http://127.0.0.1:8000/docs>

### 2. Frontend (React + Vite)

Requires Node.js 20.19+ (developed on Node 24). In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173> and you should see:

- a green **Live · backend connected** pill in the header,
- 9 room cards from SQLite, each badged `UNKNOWN`,
- `—` in the Available / Occupied / Reserved cards,
- working building / room type / minimum capacity filters,
- and, if you stop the backend and reload, an error panel with a **Try again**
  button instead of empty room cards.

`npm run build` produces a production build in `frontend/dist`.

Development requests to `/api/...` are forwarded to `http://127.0.0.1:8000` by the
Vite proxy configured in `frontend/vite.config.js`. The backend also allows the dev
origin via CORS (`ROOMPULSE_CORS_ORIGINS`).

### 3. Backend tests

```powershell
cd backend
pip install -r requirements-dev.txt
python -m pytest -q
```

The tests build a temporary SQLite database per test from the same models and seed
data the app uses, so they never touch your local `roompulse.db`.

## Configuration

| Variable | Where | Default | Purpose |
| --- | --- | --- | --- |
| `ROOMPULSE_ENV` | backend | `development` | Reported in `/api/health` |
| `ROOMPULSE_DB_PATH` | backend | `backend/roompulse.db` | Where the SQLite file lives |
| `ROOMPULSE_CORS_ORIGINS` | backend | `http://localhost:5173,http://127.0.0.1:5173` | Allowed browser origins |
| `VITE_API_BASE_URL` | frontend | `/api` | API prefix used by the frontend |

## Roadmap

1. ~~SQLite + room and timetable models, small deterministic seed data~~ (stage 2)
2. Availability engine with explicit precedence rules + unit tests, using
   timetable and capacity first; `UNKNOWN` for anything it cannot decide.
3. Occupancy simulator emitting changing sensor readings + sensor freshness
   detection.
4. WebSocket push of room states, so the dashboard is live instead of one fetch.
5. Availability-aware "Find Me a Room" filtering and explainable status details.
6. Reservations with interval-conflict checking, post-class observation window,
   concurrency-safe claims.

## Project rules

- Build incrementally, one small stage at a time.
- Keep every part simple enough to explain to a beginner.
- Availability is derived, never stored.
- No feature is claimed until it is actually implemented.


