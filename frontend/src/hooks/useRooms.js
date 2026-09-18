import { useCallback, useEffect, useState } from "react";

import { getRooms } from "../api/client.js";

/**
 * Loads the plain room catalogue from /api/rooms (rooms + timetable, no
 * derived availability), and lets the user retry after a failure.
 *
 * The dashboard currently reads /api/rooms/availability instead, so this
 * hook is unused — it stays as a tiny documented helper for the browser
 * console or a future catalogue view.
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