import { useCallback, useEffect, useState } from "react";

import { getRooms } from "../api/client.js";

/**
 * Loads the room catalogue from /api/rooms, and lets the user retry after a
 * failure (for example when the backend was not running yet).
 *
 * The rooms do not change while the page is open, so one request is enough for
 * this stage. When the availability engine and the occupancy simulator exist,
 * this hook is where the WebSocket connection will live.
 *
 * @returns {{
 *   status: "loading" | "ready" | "error",
 *   rooms: object[],
 *   error: string|null,
 *   reload: () => void,
 * }}
 */
export function useRooms() {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({
    status: "loading",
    rooms: [],
    error: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading", rooms: [], error: null });

    getRooms(controller.signal)
      .then((rooms) => {
        setState({ status: "ready", rooms, error: null });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ status: "error", rooms: [], error: error.message });
        }
      });

    return () => controller.abort();
  }, [attempt]);

  const reload = useCallback(() => setAttempt((value) => value + 1), []);

  return { ...state, reload };
}