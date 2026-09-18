import StatusLegend from "./StatusLegend.jsx";

/**
 * Where the room cards will be listed.
 *
 * There is no room data source yet, so this section shows an empty state
 * instead of made-up rooms. The legend underneath documents the states the
 * engine will return.
 */
export default function RoomResults() {
  return (
    <section className="panel results" aria-labelledby="results-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="results-heading">
          Rooms
        </h2>
        <p className="panel__note">
          0 rooms shown — RoomPulse is not connected to a room data source yet.
        </p>
      </div>

      <div className="empty-state">
        <span className="empty-state__icon" aria-hidden="true">
          <svg viewBox="0 0 64 64" width="52" height="52">
            <rect
              x="8"
              y="16"
              width="34"
              height="34"
              rx="6"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
            />
            <path
              d="M42 30h8a4 4 0 0 1 4 4v16h-12"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <path
              d="M20 16V9h12v7"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="30" cy="34" r="3" fill="currentColor" />
          </svg>
        </span>

        <h3 className="empty-state__title">No room status yet</h3>
        <p className="empty-state__body">
          The dashboard shell is ready and waiting. Room records, the
          availability engine and the occupancy simulator arrive in the next
          stages, and their output will appear right here.
        </p>
      </div>

      <StatusLegend />
    </section>
  );
}