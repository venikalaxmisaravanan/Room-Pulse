// Every backend call goes through this module so there is exactly one place to
// change the API location later (a deployed backend, a different port, ...).
//
// "/api" works out of the box because Vite proxies that prefix to FastAPI
// during development (see vite.config.js).

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

/**
 * Ask the backend whether it is running.
 * @param {AbortSignal} [signal] lets the caller cancel the request on unmount.
 */
export async function getHealth(signal) {
  const response = await fetch(`${API_BASE_URL}/health`, { signal });

  if (!response.ok) {
    throw new Error(`Backend responded with status ${response.status}`);
  }

  return response.json();
}

/**
 * Load the current availability: every room with its derived AVAILABLE /
 * IN_CLASS state at the server's current time.
 *
 * The response has the shape
 * { evaluated_at, count, available_count, in_class_count, rooms: [...] }.
 * The whole payload is returned (not just the list) because the dashboard
 * needs the counts and the evaluated moment too.
 *
 * The dashboard loads this once on startup and then refreshes whenever the
 * caller explicitly asks for a reload. The response includes the room-state
 * counts and the evaluated timestamp that the UI displays.
 *
 * @param {AbortSignal} [signal] lets the caller cancel the request on unmount.
 */
export async function getAvailability(signal) {
  const response = await fetch(`${API_BASE_URL}/rooms/availability`, { signal });

  if (!response.ok) {
    throw new Error(`/api/rooms/availability responded with status ${response.status}`);
  }

  return response.json();
}

/**
 * Load the plain room catalogue: rooms with the timetable slots that belong
 * to them, without any derived availability.
 *
 * The dashboard no longer needs this (it reads /api/rooms/availability),
 * but the helper stays so the catalogue endpoint remains easy to use from
 * the browser console or a future view.
 *
 * @param {AbortSignal} [signal] lets the caller cancel the request on unmount.
 */
export async function getRooms(signal) {
  const response = await fetch(`${API_BASE_URL}/rooms`, { signal });

  if (!response.ok) {
    throw new Error(`/api/rooms responded with status ${response.status}`);
  }

  const payload = await response.json();
  return payload.rooms ?? [];
}