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