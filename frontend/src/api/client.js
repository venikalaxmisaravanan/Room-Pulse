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
 * Load the room catalogue: every room with the timetable slots that belong to it.
 *
 * The response has the shape { count, rooms: [...] }. The list is returned
 * directly because the dashboard only needs the rooms themselves.
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