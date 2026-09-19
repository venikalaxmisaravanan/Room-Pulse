import { ROOM_STATES } from "../constants/roomStates.js";

const STATE_BY_ID = Object.fromEntries(
  ROOM_STATES.map((state) => [state.id, state])
);

const MAX_VISIBLE_SLOTS = 3;

/** The API sends ISO times ("09:00:00"); the card only needs "09:00". */
function formatTime(value) {
  return value.slice(0, 5);
}

/** "Monday" -> "Mon" so a timetable line fits on one row. */
function shortDay(day) {
  return day.slice(0, 3);
}

function formatAge(seconds) {
  if (seconds < 60) return `${seconds} second${seconds === 1 ? "" : "s"} ago`;
  const minutes = Math.floor(seconds / 60);
  return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
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
 * One room with its derived availability.
 *
 * `state` and `reason` come from GET /api/rooms/availability. Search adds a
 * separate usability explanation when the current headcount leaves room for
 * the requested group.
 */
export default function RoomCard({ room }) {
  const state = STATE_BY_ID[room.state] ?? STATE_BY_ID.UNKNOWN;

  return (
    <article className="room-card">
      <div className="room-card__top">
        <div>
          <h3 className="room-card__code">{room.code}</h3>
          <p className="room-card__name">{room.name}</p>
        </div>

        <span
          className={`badge badge--${state.tone}`}
          title={room.reason}
        >
          {state.label}
        </span>
      </div>

      <StatusExplanation room={room} />

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

function StatusExplanation({ room }) {
  const freshness = room.sensor_freshness;
  const occupancy = room.occupancy;

  return (
    <div className="room-card__explanation">
      {room.state === "IN_CLASS" && room.active_class && (
        <p>
          <strong>Class:</strong> {room.active_class.course_name} ·{" "}
          {formatTime(room.active_class.start_time)}–
          {formatTime(room.active_class.end_time)}
        </p>
      )}

      {(room.state === "OCCUPIED" || room.state === "FULL") && occupancy && (
        <p>
          <strong>Occupancy:</strong> {occupancy.occupancy} / {occupancy.capacity} people
        </p>
      )}

      {room.state === "OCCUPIED" && occupancy && (
        <p>
          <strong>Seats available:</strong> {occupancy.remaining_capacity}
        </p>
      )}

      {room.state === "UNKNOWN" && (
        <p>
          <strong>Sensor:</strong>{" "}
          {freshness?.status === "STALE" ? "Data is stale" : "Data is unavailable"}
          {freshness && ` · ${formatAge(freshness.age_seconds)}`}
        </p>
      )}

      {room.state === "AVAILABLE" && (
        <p>
          <strong>Evidence:</strong> No active class or blocking occupancy detected
        </p>
      )}

      {freshness?.fresh && room.state !== "IN_CLASS" && (
        <p>
          <strong>Sensor:</strong> Updated {formatAge(freshness.age_seconds)}
        </p>
      )}

      {room.usability_reason && (
        <p>
          <strong>Search:</strong> {room.usability_reason}
        </p>
      )}

      <p className="room-card__why">
        <strong>Why:</strong> {room.reason}
      </p>
    </div>
  );
}