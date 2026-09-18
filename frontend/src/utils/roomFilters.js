// Filtering over the latest complete availability snapshot.

export const EMPTY_FILTERS = { building: "", roomType: "", minCapacity: "" };

/**
 * Build the option lists for the filter controls from the loaded rooms,
 * so the dropdowns can never offer a value that has no rooms.
 */
export function getFilterOptions(rooms) {
  return {
    buildings: [...new Set(rooms.map((room) => room.building))].sort(),
    roomTypes: [...new Set(rooms.map((room) => room.room_type))].sort(),
  };
}

/**
 * Apply the three filters to the catalogue.
 * An empty value means "no restriction on this field".
 */
export function filterRooms(rooms, filters) {
  const minCapacity = Number.parseInt(filters.minCapacity, 10);

  return rooms.filter((room) => {
    if (room.state !== "AVAILABLE") {
      return false;
    }
    if (filters.building && room.building !== filters.building) {
      return false;
    }
    if (filters.roomType && room.room_type !== filters.roomType) {
      return false;
    }
    if (!Number.isNaN(minCapacity) && room.capacity < minCapacity) {
      return false;
    }
    return true;
  });
}

/** True when at least one filter is set (used to show the reset button). */
export function hasActiveFilters(filters) {
  return Boolean(filters.building || filters.roomType || filters.minCapacity);
}

export function describeFilters(filters) {
  const building = filters.building || "any building";
  const roomType = filters.roomType
    ? `${filters.roomType.toLowerCase()} rooms`
    : "rooms";
  const capacity = filters.minCapacity
    ? `at least ${filters.minCapacity} seats`
    : "any capacity";
  return `${building} ${roomType} with ${capacity}`;
}