import { ACTIVE_STATES, ROOM_STATES } from "../constants/roomStates.js";

/**
 * Explains the colour of each room state.
 *
 * Badges marked "(live)" are decided by the timetable engine right now;
 * the rest are the vocabulary later stages will fill in (occupancy,
 * reservations, sensor freshness).
 */
export default function StatusLegend() {
  return (
    <section className="panel legend" aria-labelledby="legend-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="legend-heading">
          What the badges mean
        </h2>
        <p className="panel__note">
          Available and In class are derived from the timetable at the
          evaluated moment. Occupancy, reservations and sensor freshness
          arrive in later stages — never from one boolean flag.
        </p>
      </div>

      <ul className="legend__list">
        {ROOM_STATES.map((state) => (
          <li key={state.id} className="legend__item">
            <span className={`badge badge--${state.tone}`}>
              {state.label}
            </span>
            <span className="legend__description">
              {state.description}{" "}
              {ACTIVE_STATES.has(state.id) ? (
                <em className="legend__live">(live in stage 3)</em>
              ) : (
                <em className="legend__live">(later stage)</em>
              )}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}