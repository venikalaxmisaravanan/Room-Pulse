import { ROOM_STATES } from "../constants/roomStates.js";

const UNKNOWN_STATE = ROOM_STATES.find((state) => state.id === "UNKNOWN");
const MAX_VISIBLE_SLOTS = 3;

/** The API sends ISO times ("09:00:00"); the card only needs "09:00". */
function formatTime(value) {
  return value.slice(0, 5);
}

/** "Monday" -> "Mon" so a timetable line fits on one row. */
function shortDay(day) {
  return day.slice(0, 3);
}

function TimetableList({ slots }) {
  if (slots.length === 0) {
    return (
      <p className="timetable__empty">
        No classes in the prototype timetable — that does not mean the room is
        free, because availability is not calculated yet.
      </p>
    );
  }

  const visible = slots.slice(0, MAX_VISIBLE_SLOTS);
  const hiddenCount = slots.length - visible.length;

  return (
    <>
      <ul className="timetable">
        {visible.map((slot) => (
          <li className="timetable__item" key={slot.id}>
            <span className="timetable__when">
              {shortDay(slot.day_of_week)} {formatTime(slot.start_time)}–
              {formatTime(slot.end_time)}
            </span>
            <span className="timetable__course">{slot.course_name}</span>
          </li>
        ))}
      </ul>

      {hiddenCount > 0 && (
        <p className="timetable__more">
          +{hiddenCount} more session{hiddenCount > 1 ? "s" : ""} in the
          catalogue
        </p>
      )}
    </>
  );
}

/**
 * One room from the catalogue.
 *
 * The status badge is hard-coded to UNKNOWN because the availability engine
 * does not exist yet: RoomPulse knows the timetable, but nothing turns
 * timetable + occupancy + reservations + sensor freshness into "can I use this
 * room right now?". Showing AVAILABLE here would be a lie.
 */
export default function RoomCard({ room }) {
  return (
    <article className="room-card">
      <div className="room-card__top">
        <div>
          <h3 className="room-card__code">{room.code}</h3>
          <p className="room-card__name">{room.name}</p>
        </div>

        <span
          className={`badge badge--${UNKNOWN_STATE.tone}`}
          title="Availability engine not implemented yet"
        >
          {UNKNOWN_STATE.label}
        </span>
      </div>

      <dl className="room-card__facts">
        <div className="fact">
          <dt>Building</dt>
          <dd>{room.building}</dd>
        </div>
        <div className="fact">
          <dt>Type</dt>
          <dd>{room.room_type}</dd>
        </div>
        <div className="fact">
          <dt>Capacity</dt>
          <dd>{room.capacity} seats</dd>
        </div>
      </dl>

      <div className="room-card__timetable">
        <h4 className="room-card__section-title">Timetable (prototype data)</h4>
        <TimetableList slots={room.timetable} />
      </div>
    </article>
  );
}