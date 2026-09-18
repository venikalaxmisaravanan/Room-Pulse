"""Live evaluation loop backing the RoomPulse WebSocket feed.

This module is intentionally thin: it reuses the existing simulator and the
existing availability evaluator, and produces exactly the same snapshot shape
as the REST `/api/rooms/availability` endpoint so the frontend never has to
translate between the two paths.

Lifecycle:
- There is one shared live loop, started when the first WebSocket client
  connects and stopped when the last one leaves.
- Each iteration advances the simulator by one tick, evaluates the catalogue
  at the resulting time, and pushes one snapshot to every connected client.
- Snapshots are sent on every iteration so the feed feels live even when only
  some rooms change; the small sleep interval keeps traffic modest.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass
from typing import Any

from app.services.availability_service import evaluate_catalogue_from_simulator
from app.services.occupancy import (
    current_evaluated_at,
)
from app.services.occupancy import current_occupancy
from app.services.occupancy import init_occupancy_jsim_for_loop
from app.services.occupancy import advance_simulation_one_tick


# ---------------------------------------------------------------------------
# Container / lifecycle
# ---------------------------------------------------------------------------

@dataclass
class SimulationLoop:
    """One shared loop context."""

    started_at: float = _time.time()
    tick: int = 0

    def advance(self, steps: int = 1) -> None:
        self.tick += steps

    def snapshot(self) -> dict[str, Any]:
        t = current_evaluated_at()
        return evaluate_catalogue_from_simulator(t)


def start_loop() -> SimulationLoop:
    """Prepare the shared loop and ensure JSim state is initialized."""
    loop = SimulationLoop()
    init_occupancy_jsim_for_loop()
    return loop


# ---------------------------------------------------------------------------
# Per-iteration helpers used by the WebSocket handler
# ---------------------------------------------------------------------------


def tick_loop(loop: SimulationLoop) -> None:
    advance_simulation_one_tick()
    loop.advance(1)
