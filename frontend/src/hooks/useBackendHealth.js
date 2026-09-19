import { useEffect, useState } from "react";

import { getHealth } from "../api/client.js";

/**
 * Asks the backend once, on page load, whether it is alive.
 *
 * This hook is intentionally small: the dashboard reports backend health
 * separately from the live WebSocket connection state.
 *
 * @returns {{ state: "checking" | "online" | "offline", details: object|null, error: string|null }}
 */
export function useBackendHealth() {
  const [health, setHealth] = useState({
    state: "checking",
    details: null,
    error: null,
  });

  useEffect(() => {
    const controller = new AbortController();

    getHealth(controller.signal)
      .then((details) => {
        setHealth({ state: "online", details, error: null });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setHealth({ state: "offline", details: null, error: error.message });
        }
      });

    return () => controller.abort();
  }, []);

  return health;
}