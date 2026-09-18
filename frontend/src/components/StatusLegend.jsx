import { ROOM_STATES } from "../constants/roomStates.js";

/**
 * Explains the colour of each room state.
 *
 * This is documentation inside the UI, not state logic: the availability
 * engine decides which state a room is in, and this legend keeps the colours
 * consistent with the cards that will render those decisions.
 */
export default function StatusLegend() {
  return (
    <section className="panel legend" aria-labelledby="legend-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="legend-heading">
          What the badges will mean
        </h2>
        <p className="panel__note">
          Room status is derived later from timetable, occupancy, reservations
          and sensor freshness — never from one boolean flag.
        </p>
      </div>

      <ul className="legend__list">
        {ROOM_STATES.map((state) => (
          <li key={state.id} className="legend__item">
            <span className={`badge badge--${state.tone}`}>{state.label}</span>
            <span className="legend__description">{state.description}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}