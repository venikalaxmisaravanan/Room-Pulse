// The six room states the availability engine will produce later.
//
// Nothing calculates these states yet — the dashboard only uses this list to
// show the legend, so the colours are already fixed and consistent when the
// engine starts returning real values.

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