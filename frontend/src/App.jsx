import { useMemo, useState } from "react";

import FiltersBar from "./components/FiltersBar.jsx";
import HeaderBar from "./components/HeaderBar.jsx";
import RoomResults from "./components/RoomResults.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import { useRooms } from "./hooks/useRooms.js";
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
 *   /api/rooms (SQLite) -> useRooms -> filterRooms -> RoomResults -> RoomCard
 *
 * Every room is shown as UNKNOWN because the availability engine does not exist
 * yet; this stage only proves that real room and timetable data reaches the UI.
 */
export default function App() {
  const { status, rooms, error, reload } = useRooms();
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

        <SummaryCards />

        <RoomResults
          rooms={visibleRooms}
          totalRooms={rooms.length}
          status={status}
          error={error}
          onRetry={reload}
        />
      </main>

      <footer className="app__footer">
        <span>RoomPulse · stage 2: room catalogue + timetable from SQLite</span>
        <span className="app__footer-api">
          API endpoints: <code>/api/health</code> · <code>/api/rooms</code>
        </span>
      </footer>
    </div>
  );
}