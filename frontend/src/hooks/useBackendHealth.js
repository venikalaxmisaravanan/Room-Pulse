import { useEffect, useState } from "react";

import { getHealth } from "../api/client.js";

/**
 * Asks the backend once, on page load, whether it is alive.
 *
 * One request is enough for this stage: the dashboard has no live data to
 * stream yet. Real-time updates (WebSocket) are a later stage, which is why
 * this hook is kept deliberately small and easy to replace.
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