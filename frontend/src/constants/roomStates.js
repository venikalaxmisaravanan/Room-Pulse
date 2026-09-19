export const ROOM_STATES = [
  {
    id: "AVAILABLE",
    label: "Available",
    tone: "available",
    description:
      "No class is scheduled and the room has no trusted occupancy.",
  },
  {
    id: "OCCUPIED",
    label: "Occupied",
    tone: "occupied",
    description:
      "People are inside and no class is scheduled. Remaining seats may still be available.",
  },
  {
    id: "IN_CLASS",
    label: "In class",
    tone: "in-class",
    description: "A scheduled class is currently in progress.",
  },
  {
    id: "FULL",
    label: "Full",
    tone: "full",
    description: "Trusted occupancy has reached the room capacity.",
  },
  {
    id: "UNKNOWN",
    label: "Unknown",
    tone: "unknown",
    description:
      "Sensor data is stale or unavailable, so RoomPulse cannot safely determine usability.",
  },
];