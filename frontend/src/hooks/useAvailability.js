import { useCallback, useEffect, useState } from "react";

import { getAvailability } from "../api/client.js";

/**
 * Loads the REST snapshot first, then replaces it with snapshots from /api/ws.
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
  const [connectionState, setConnectionState] = useState("connecting");
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

    let socket;
    let reconnectTimer;
    let stopped = false;
    let hasConnected = false;

    const connect = () => {
      if (stopped) return;
      setConnectionState(hasConnected ? "reconnecting" : "connecting");
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${protocol}://${window.location.host}/api/ws`);
      socket.onopen = () => {
        hasConnected = true;
        setConnectionState("connected");
      };
      socket.onmessage = ({ data }) => {
        const payload = JSON.parse(data);
        if (!payload.rooms) return;
        setState({
          status: "ready",
          rooms: payload.rooms,
          availableCount: payload.available_count ?? null,
          inClassCount: payload.in_class_count ?? null,
          evaluatedAt: payload.evaluated_at ?? null,
          error: null,
        });
      };
      socket.onclose = () => {
        if (!stopped) {
          setConnectionState(hasConnected ? "reconnecting" : "disconnected");
          reconnectTimer = window.setTimeout(connect, 1000);
        }
      };
      socket.onerror = () => socket.close();
    };
    connect();

    return () => {
      stopped = true;
      controller.abort();
      window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [attempt]);

  const reload = useCallback(() => setAttempt((value) => value + 1), []);

  return { ...state, reload, connectionState };
}
