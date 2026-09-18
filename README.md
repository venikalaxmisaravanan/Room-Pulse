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

Room availability is **derived, not stored**. There is no `available = true`
column anywhere in this project. Instead, every room has several changing inputs,
and one deterministic availability engine turns them into one current state:

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

## Planned architecture

| Layer | Choice | Notes |
| --- | --- | --- |
| Frontend | React (Vite, plain JavaScript) | Dashboard shell; real-time updates via WebSocket later |
| Backend | Python + FastAPI | REST under `/api`, WebSocket later |
| Database | SQLite | Rooms, timetable, reservations, occupancy readings |
| Simulation | Python | Occupancy simulator that emits changing sensor readings |

```
RoomPulse/
├── backend/          FastAPI app (routes, schemas, models, services)
└── frontend/         React dashboard
```

## MVP feature list

Must-have (planned, not all implemented):

1. Multi-source availability engine
2. Deterministic conflict / precedence rules
3. Dynamic occupancy simulator
4. Sensor freshness / stale-data detection
5. Real-time dashboard
6. Explainable room status
7. Capacity-aware availability
8. "Find Me a Room" filtering / query

If time permits later:

9. Post-class observation window
10. Faculty reservation with interval-conflict checking
11. Concurrency-safe room claims

## Current implementation status

### Implemented (stage 1 — project foundation + UI shell)

- FastAPI backend that starts with one endpoint: `GET /api/health`, returning
  JSON (`status`, `service`, `version`, `environment`, `checked_at`).
- Backend folder structure ready for later modules:
  `app/api/routes/`, `app/schemas/`, `app/models/`, `app/services/`, `app/core/`.
- React + Vite dashboard shell: RoomPulse branding, product tagline, header
  status indicator wired to the real `/api/health` endpoint, disabled filter
  placeholders (building, room type, minimum capacity), Available / Occupied /
  Reserved summary cards, room-results section with an empty state, and a legend
  of the six future room states.
- Vite dev proxy so the frontend calls `/api/...` on its own origin.

### Not implemented yet (planned)

- Availability engine and any room-state logic (the state names exist only as
  UI legend text).
- Room / timetable / reservation / occupancy models and SQLite storage.
- Occupancy simulator, sensor freshness detection, capacity-aware logic.
- Real-time WebSocket updates (the header indicator does a single health check).
- "Find Me a Room" filtering (the filter controls are deliberately disabled).
- Reservations, concurrency-safe claims, post-class observation window.
- Authentication, student/faculty accounts, CCTV/computer vision, notifications,
  chatbot, mobile app — explicitly out of scope for this project.
- No room records exist yet on purpose: the dashboard shows an honest empty state
  rather than fake rooms.

## Local setup and run instructions

Two terminals. Backend first, then frontend.

### 1. Backend (FastAPI)

Requires Python 3.9+ (developed on 3.11).

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify it:

- Health check: <http://127.0.0.1:8000/api/health>
- Interactive API docs: <http://127.0.0.1:8000/docs>

Expected `/api/health` response:

```json
{
  "status": "ok",
  "service": "RoomPulse API",
  "version": "0.1.0",
  "environment": "development",
  "checked_at": "2026-01-01T10:00:00Z"
}
```

### 2. Frontend (React + Vite)

Requires Node.js 20.19+ (developed on Node 24). In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

- The header pill shows a green **Live · backend connected** state when the
  backend is running, and red when it is not.
- Filters and summary values are placeholders until the data and availability
  stages are done.
- `npm run build` produces a production build in `frontend/dist`.

Development requests to `/api/...` are forwarded to `http://127.0.0.1:8000` by
the Vite proxy configured in `frontend/vite.config.js`. The backend also allows
the dev origin via CORS (`ROOMPULSE_CORS_ORIGINS`).

## Configuration

| Variable | Where | Default | Purpose |
| --- | --- | --- | --- |
| `ROOMPULSE_ENV` | backend | `development` | Reported in `/api/health` |
| `ROOMPULSE_CORS_ORIGINS` | backend | `http://localhost:5173,http://127.0.0.1:5173` | Allowed browser origins |
| `VITE_API_BASE_URL` | frontend | `/api` | API prefix used by the frontend |

## Roadmap for the next stages

1. SQLite + room and timetable models (real, if small, seed data).
2. Availability engine with explicit precedence rules and unit tests.
3. Occupancy simulator + sensor freshness handling.
4. WebSocket push of room states and the real-time dashboard.
5. "Find Me a Room" filtering and explainable status details.

## Project rules

- Build incrementally, one small stage at a time.
- Keep every part simple enough to explain to a beginner.
- No feature is claimed until it is actually implemented.
