import RoomCard from "./RoomCard.jsx";
import StatusLegend from "./StatusLegend.jsx";

/** The sentence in the panel header, which changes with the data situation. */
function describeResults({ status, totalRooms, shownCount, evaluatedAt }) {
  if (status === "loading") {
    return "Loading current availability from /api/rooms/availability …";
  }
  if (status === "error") {
    return "Availability unavailable.";
  }
  if (totalRooms === 0) {
    return "The room catalogue is empty.";
  }
  const shown = `${shownCount} of ${totalRooms} rooms shown`;
  if (evaluatedAt) {
    return `${shown} · evaluated at ${formatEvaluatedAt(evaluatedAt)}.`;
  }
  return `${shown} · states derived from the timetable.`;
}

/** "2026-09-21T12:00:00" -> "Mon 12:00" for the panel header. */
function formatEvaluatedAt(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value.slice(0, 16).replace("T", " ");
  }
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${days[date.getDay()]} ${hours}:${minutes}`;
}

/** The three data situations (loading, failure, empty) plus the room grid. */
function ResultsBody({ rooms, totalRooms, status, error, onRetry, searched, searchDescription }) {
  if (status === "loading") {
    return (
      <div className="data-state">
        <h3 className="data-state__title">Loading rooms…</h3>
        <p className="data-state__body">Waiting for /api/rooms/availability to answer.</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="data-state data-state--error" role="alert">
        <h3 className="data-state__title">Could not load room availability</h3>
        <p className="data-state__body">
          The request to <code>/api/rooms/availability</code> failed: {error}
        </p>
        <p className="data-state__body">
          Check that the FastAPI backend is running on{" "}
          <code>http://127.0.0.1:8000</code>, then try again.
        </p>
        <button type="button" className="data-state__action" onClick={onRetry}>
          Try again
        </button>
      </div>
    );
  }

  if (totalRooms === 0) {
    return (
      <div className="empty-state">
        <h3 className="empty-state__title">The room catalogue is empty</h3>
        <p className="empty-state__body">
          The backend answered, but no rooms are stored in SQLite yet. Create and
          seed the database with <code>python -m app.db.init_db</code> from the{" "}
          <code>backend</code> folder.
        </p>
      </div>
    );
  }

  if (rooms.length === 0) {
    return (
      <div className="empty-state">
        <h3 className="empty-state__title">
          {searched ? "No usable rooms found" : "No rooms match your filters"}
        </h3>
        <p className="empty-state__body">
          {searched
            ? `No ${searchDescription} are currently usable. Try a different building, room type or a smaller minimum capacity.`
            : "Every room in the loaded catalogue was filtered out. Change the building, room type or minimum capacity to see rooms again."}
        </p>
      </div>
    );
  }

  return (
    <div className="room-grid">
      {rooms.map((room) => (
        <RoomCard key={room.id} room={room} />
      ))}
    </div>
  );
}

/**
 * The room results area: real AVAILABLE / IN_CLASS answers from the engine.
 *
 * The component never invents data. While loading it says so, if the request
 * fails it explains why, and each room card carries the state the engine
 * derived from that room's timetable at the evaluated moment.
 */
export default function RoomResults({
  rooms,
  totalRooms,
  status,
  error,
  evaluatedAt,
  onRetry,
  searched,
  searchDescription,
}) {
  return (
    <section className="panel results" aria-labelledby="results-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="results-heading">
          Rooms
        </h2>
        <p className="panel__note">
          {describeResults({ status, totalRooms, shownCount: rooms.length, evaluatedAt })}
        </p>
      </div>

      {status === "ready" && totalRooms > 0 && (
        <p className="results__notice">
          <strong>Derived, not stored.</strong> Each badge comes from the
          timetable at the evaluated moment: a room with a class in session
          is <strong>In class</strong>, otherwise it is{" "}
          <strong>Available</strong>. AVAILABLE means “no class scheduled” —
          RoomPulse has no occupancy sensors yet, so it cannot promise the
          room is actually empty.
        </p>
      )}

      <ResultsBody
        rooms={rooms}
        totalRooms={totalRooms}
        status={status}
        error={error}
        onRetry={onRetry}
        searched={searched}
        searchDescription={searchDescription}
      />

      <StatusLegend />
    </section>
  );
}