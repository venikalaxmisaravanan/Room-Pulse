import { useMemo, useState } from "react";

import FiltersBar from "./components/FiltersBar.jsx";
import HeaderBar from "./components/HeaderBar.jsx";
import RoomResults from "./components/RoomResults.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import { useAvailability } from "./hooks/useAvailability.js";
import {
  EMPTY_FILTERS,
  filterRooms,
  getFilterOptions,
  hasActiveFilters,
} from "./utils/roomFilters.js";

/**
 * RoomPulse dashboard.
 *
 * Data flows in one direction:
 *   SQLite -> /api/rooms/availability (engine: timetable x now)
 *     -> useAvailability -> filterRooms -> RoomResults -> RoomCard
 *
 * Every badge is derived: AVAILABLE means no class is in session at the
 * evaluated moment, IN_CLASS means a timetable slot is active.
 */
export default function App() {
  const {
    status,
    rooms,
    availableCount,
    inClassCount,
    evaluatedAt,
    error,
    reload,
  } = useAvailability();
  const [filters, setFilters] = useState(EMPTY_FILTERS);

  const options = useMemo(() => getFilterOptions(rooms), [rooms]);
  const visibleRooms = useMemo(
    () => filterRooms(rooms, filters),
    [rooms, filters]
  );

  return (
    <div className="app">
      <HeaderBar />

      <main className="app__main">
        <FiltersBar
          filters={filters}
          onChange={setFilters}
          options={options}
          disabled={status !== "ready" || rooms.length === 0}
          showReset={hasActiveFilters(filters)}
        />

        <SummaryCards
          availableCount={availableCount}
          inClassCount={inClassCount}
        />

        <RoomResults
          rooms={visibleRooms}
          totalRooms={rooms.length}
          status={status}
          error={error}
          evaluatedAt={evaluatedAt}
          onRetry={reload}
        />
      </main>

      <footer className="app__footer">
        <span>RoomPulse · stage 3: timetable availability engine</span>
        <span className="app__footer-api">
          API endpoints: <code>/api/health</code> · <code>/api/rooms</code> ·{" "}
          <code>/api/rooms/availability</code>
        </span>
      </footer>
    </div>
  );
}