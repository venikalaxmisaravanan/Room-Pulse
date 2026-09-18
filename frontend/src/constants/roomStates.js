// The room states the Stage 3 engine can produce.
//
// AVAILABLE and IN_CLASS are real: they are derived from the timetable and
// the current time by GET /api/rooms/availability.
//
// OCCUPIED, RESERVED, FULL and UNKNOWN are future states (occupancy sensors,
// reservations, sensor freshness). They are defined here so the legend can
// teach the colour vocabulary early, before the later stages start using it.

export const ACTIVE_STATES = new Set(["AVAILABLE", "IN_CLASS"]);

export const ROOM_STATES = [
  {
    id: "AVAILABLE",
    label: "Available",
    tone: "available",
    description: "Free to use right now.",
  },
  {
    id: "OCCUPIED",
    label: "Occupied",
    tone: "occupied",
    description: "People are inside; no class is scheduled.",
  },
  {
    id: "IN_CLASS",
    label: "In class",
    tone: "in-class",
    description: "The timetable shows a class in session.",
  },
  {
    id: "RESERVED",
    label: "Reserved",
    tone: "reserved",
    description: "Held for a faculty reservation.",
  },
  {
    id: "FULL",
    label: "Full",
    tone: "full",
    description: "Occupancy has reached capacity.",
  },
  {
    id: "UNKNOWN",
    label: "Unknown",
    tone: "unknown",
    description: "Sensor data is stale or sources disagree.",
  },
];