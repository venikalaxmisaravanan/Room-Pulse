// Filtering over the loaded room catalogue.
//
// The catalogue is one campus (9 rooms), so filtering in the browser needs no
// extra backend endpoint. When the "Find Me a Room" stage adds availability to
// the question, this logic moves to the API instead.

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