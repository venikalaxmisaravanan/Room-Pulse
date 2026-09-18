import { useCallback, useEffect, useState } from "react";

import { getAvailability } from "../api/client.js";

/**
 * Loads the current availability from /api/rooms/availability, and lets the
 * user retry after a failure (for example when the backend was not running).
 *
 * The engine evaluates the timetable once per request on the server, so one
 * request on page load is enough for this stage. There is no live sensor
 * stream yet, so there is deliberately no polling or WebSocket here —
 * this hook is where the WebSocket connection will live in a later stage.
 *
 * @returns {{
 *   status: "loading" | "ready" | "error",
 *   rooms: object[],
 *   availableCount: number|null,
 *   inClassCount: number|null,
 *   evaluatedAt: string|null,
 *   error: string|null,
 *   reload: () => void,
 * }}
 */
export function useAvailability() {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({
    status: "loading",
    rooms: [],
    availableCount: null,
    inClassCount: null,
    evaluatedAt: null,
    error: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({
      status: "loading",
      rooms: [],
      availableCount: null,
      inClassCount: null,
      evaluatedAt: null,
      error: null,
    });

    getAvailability(controller.signal)
      .then((payload) => {
        setState({
          status: "ready",
          rooms: payload.rooms ?? [],
          availableCount: payload.available_count ?? null,
          inClassCount: payload.in_class_count ?? null,
          evaluatedAt: payload.evaluated_at ?? null,
          error: null,
        });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({
            status: "error",
            rooms: [],
            availableCount: null,
            inClassCount: null,
            evaluatedAt: null,
            error: error.message,
          });
        }
      });

    return () => controller.abort();
  }, [attempt]);

  const reload = useCallback(() => setAttempt((value) => value + 1), []);

  return { ...state, reload };
}
