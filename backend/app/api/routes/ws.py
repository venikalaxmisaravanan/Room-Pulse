"""Live availability snapshots for the dashboard WebSocket."""

from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.core.config import WS_UPDATE_INTERVAL_SECONDS
from app.services.availability_service import evaluate_catalogue_from_simulator
from app.services.occupancy import (
    advance_simulation_one_tick,
    current_evaluated_at,
    init_occupancy_jsim_for_loop,
)

router = APIRouter(tags=["live"])


class ConnectionBag:
    """Own one simulator loop and broadcast each full snapshot to all clients."""

    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()
        self.task: asyncio.Task[None] | None = None

    def add(self, websocket: WebSocket) -> None:
        self.connections.add(websocket)
        if self.task is None or self.task.done():
            init_occupancy_jsim_for_loop()
            self.task = asyncio.create_task(self.run())

    def remove(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)
        if not self.connections and self.task is not None and not self.task.done():
            self.task.cancel()

    async def run(self) -> None:
        try:
            while self.connections:
                evaluated_at = datetime.now()
                advance_simulation_one_tick()
                snapshot = evaluate_catalogue_from_simulator(
                    evaluated_at, occupancy_now=current_evaluated_at()
                )
                payload = snapshot.model_dump(mode="json")
                for websocket in tuple(self.connections):
                    try:
                        if websocket.client_state is WebSocketState.CONNECTED:
                            await websocket.send_json(payload)
                    except Exception:
                        self.connections.discard(websocket)
                await asyncio.sleep(WS_UPDATE_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            pass
        finally:
            self.task = None


_connections = ConnectionBag()


@router.websocket("/ws")
async def roompulse_live_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    _connections.add(websocket)
    try:
        await websocket.send_json(
            {"meta": {"kind": "connected", "connected": True}}
        )
        while websocket.client_state is WebSocketState.CONNECTED:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        _connections.remove(websocket)
