import RoomCard from "./RoomCard.jsx";
import StatusLegend from "./StatusLegend.jsx";

/** The sentence in the panel header, which changes with the data situation. */
function describeResults({ status, totalRooms, shownCount }) {
  if (status === "loading") {
    return "Loading the room catalogue from /api/rooms …";
  }
  if (status === "error") {
    return "Room catalogue unavailable.";
  }
  if (totalRooms === 0) {
    return "The room catalogue is empty.";
  }
  return `${shownCount} of ${totalRooms} rooms shown — every room is UNKNOWN until the availability engine exists.`;
}

/** The three data situations (loading, failure, empty) plus the room grid. */
function ResultsBody({ rooms, totalRooms, status, error, onRetry }) {
  if (status === "loading") {
    return (
      <div className="data-state">
        <h3 className="data-state__title">Loading rooms…</h3>
        <p className="data-state__body">Waiting for /api/rooms to answer.</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="data-state data-state--error" role="alert">
        <h3 className="data-state__title">Could not load the room catalogue</h3>
        <p className="data-state__body">
          The request to <code>/api/rooms</code> failed: {error}
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
        <h3 className="empty-state__title">No rooms match your filters</h3>
        <p className="empty-state__body">
          Every room in the loaded catalogue was filtered out. Change the
          building, room type or minimum capacity to see rooms again.
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
 * The room results area: real rooms from SQLite once /api/rooms answers.
 *
 * The component never invents data. While loading it says so, if the request
 * fails it explains why, and each room card carries the UNKNOWN badge because
 * availability is not calculated yet.
 */
export default function RoomResults({
  rooms,
  totalRooms,
  status,
  error,
  onRetry,
}) {
  return (
    <section className="panel results" aria-labelledby="results-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="results-heading">
          Rooms
        </h2>
        <p className="panel__note">
          {describeResults({ status, totalRooms, shownCount: rooms.length })}
        </p>
      </div>

      {status === "ready" && totalRooms > 0 && (
        <p className="results__notice">
          <strong>UNKNOWN is intentional.</strong> These rooms come from the
          SQLite catalogue, but the availability engine — timetable +
          occupancy + reservations + capacity + sensor freshness — is a later
          stage, so RoomPulse does not yet know which rooms you can use.
        </p>
      )}

      <ResultsBody
        rooms={rooms}
        totalRooms={totalRooms}
        status={status}
        error={error}
        onRetry={onRetry}
      />

      <StatusLegend />
    </section>
  );
}