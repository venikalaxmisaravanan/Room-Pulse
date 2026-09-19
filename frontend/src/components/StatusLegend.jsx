import { ROOM_STATES } from "../constants/roomStates.js";

/**
 * Explains the current room-state vocabulary used by the live availability
 * response and the search logic.
 */
export default function StatusLegend() {
  return (
    <section className="panel legend" aria-labelledby="legend-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="legend-heading">
          What the badges mean
        </h2>
        <p className="panel__note">
          Room states combine timetable, occupancy and sensor freshness. Search
          usability is calculated separately from trusted remaining capacity.
        </p>
      </div>

      <ul className="legend__list">
        {ROOM_STATES.map((state) => (
          <li key={state.id} className="legend__item">
            <span className={`badge badge--${state.tone}`}>
              {state.label}
            </span>
            <span className="legend__description">{state.description}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}