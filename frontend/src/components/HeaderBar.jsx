const STATUS_TEXT = {
  connecting: "Connecting",
  connected: "Connected",
  reconnecting: "Reconnecting",
  disconnected: "Disconnected",
};

/**
 * Product header: branding plus a status pill.
 *
 * The pill is driven by the real /api/health call, so it tells the truth:
 * green only when FastAPI actually answered. Live room updates reuse this
 * slot in a later stage.
 */
export default function HeaderBar({ connectionState }) {
  const state = connectionState ?? "disconnected";
  const detail = state === "connected" ? "Live availability snapshots" : "Live feed /api/ws";

  return (
    <header className="header">
      <div className="header__brand">
        <span className="header__logo" aria-hidden="true">
          <svg viewBox="0 0 48 48" width="40" height="40">
            <defs>
              <linearGradient id="roompulse-logo" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#22d3ee" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
            </defs>
            <rect
              x="1.5"
              y="1.5"
              width="45"
              height="45"
              rx="13"
              fill="url(#roompulse-logo)"
            />
            <path
              d="M7 26h7l3.5-9 6.5 16 4-11 3 4h10"
              fill="none"
              stroke="#0b1220"
              strokeWidth="3.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>

        <div className="header__text">
          <h1 className="header__title">
            Room<span className="header__title-accent">Pulse</span>
          </h1>
          <p className="header__tagline">
            Find a room you can actually use right now.
          </p>
        </div>
      </div>

      <div
        className={`status-pill status-pill--${state}`}
        role="status"
        aria-live="polite"
      >
        <span className="status-pill__dot" aria-hidden="true" />
        <span className="status-pill__text">
          <strong>{STATUS_TEXT[state]}</strong>
          <small>{detail}</small>
        </span>
      </div>
    </header>
  );
}