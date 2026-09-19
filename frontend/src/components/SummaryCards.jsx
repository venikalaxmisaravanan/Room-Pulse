// The two headline numbers the dashboard shows.
//
// These are the real counts returned by GET /api/rooms/availability at the
// evaluated moment — the number of rooms whose timetable says IN_CLASS,
// and the number with nothing scheduled right now (AVAILABLE).
// They are not occupancy statistics: with no sensors yet, RoomPulse cannot
// know whether an AVAILABLE room is actually empty.
// `tone` matches the room-state colours defined in constants/roomStates.js.

const SUMMARY_CARDS = [
  {
    id: "available",
    label: "Available",
    tone: "available",
    hint: "Room state: no class scheduled",
  },
  {
    id: "in-class",
    label: "In class",
    tone: "in-class",
    hint: "Room state: timetable in session",
  },
];

/**
 * Summary cards for current room-state totals.
 *
 * The values come from the availability endpoint. While the data is loading
 * or failed, an em dash is shown instead of a number so the UI does not imply
 * a fact it cannot trust.
 */
export default function SummaryCards({ availableCount, inClassCount }) {
  const values = { available: availableCount, "in-class": inClassCount };

  return (
    <section className="summary" aria-label="Room status summary">
      {SUMMARY_CARDS.map((card) => {
        const value = values[card.id];
        const display = value === null || value === undefined ? "—" : String(value);
        const accessible =
          value === null || value === undefined
            ? `${card.label}: not calculated yet`
            : `${card.label}: ${value}`;
        return (
          <article
            key={card.id}
            className={`summary-card summary-card--${card.tone}`}
          >
            <p className="summary-card__label">{card.label}</p>
            <p
              className="summary-card__value"
              title="Derived from the timetable by the availability engine"
              aria-label={accessible}
            >
              {display}
            </p>
            <p className="summary-card__hint">{card.hint}</p>
          </article>
        );
      })}
    </section>
  );
}