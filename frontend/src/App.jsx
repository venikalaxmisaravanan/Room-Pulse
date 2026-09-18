import FiltersBar from "./components/FiltersBar.jsx";
import HeaderBar from "./components/HeaderBar.jsx";
import RoomResults from "./components/RoomResults.jsx";
import SummaryCards from "./components/SummaryCards.jsx";

/**
 * RoomPulse dashboard shell.
 *
 * Layout only, in three stacked blocks:
 *   1. header with branding and the backend status indicator
 *   2. filters and the Available / Occupied / Reserved summary
 *   3. the room results area (currently an empty state)
 */
export default function App() {
  return (
    <div className="app">
      <HeaderBar />

      <main className="app__main">
        <FiltersBar />
        <SummaryCards />
        <RoomResults />
      </main>

      <footer className="app__footer">
        <span>RoomPulse · stage 1: project foundation and UI shell</span>
        <span className="app__footer-api">
          API endpoint: <code>/api/health</code>
        </span>
      </footer>
    </div>
  );
}