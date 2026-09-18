// The three headline numbers the dashboard will show.
// `tone` matches the room-state colours defined in constants/roomStates.js.

const SUMMARY_CARDS = [
  { id: "available", label: "Available", tone: "available", hint: "Free to use now" },
  { id: "occupied", label: "Occupied", tone: "occupied", hint: "In use, no class" },
  { id: "reserved", label: "Reserved", tone: "reserved", hint: "Held for later" },
];

/**
 * Summary cards for Available / Occupied / Reserved.
 *
 * The values stay em dashes: counting rooms needs the availability engine, and
 * the engine does not exist yet. Printing 0 (or a made-up number) would claim
 * knowledge RoomPulse does not have.
 */
export default function SummaryCards() {
  return (
    <section className="summary" aria-label="Room status summary">
      {SUMMARY_CARDS.map((card) => (
        <article
          key={card.id}
          className={`summary-card summary-card--${card.tone}`}
        >
          <p className="summary-card__label">{card.label}</p>
          <p
            className="summary-card__value"
            title="Counted by the availability engine, which is not implemented yet"
            aria-label={`${card.label}: not calculated yet`}
          >
            —
          </p>
          <p className="summary-card__hint">{card.hint}</p>
        </article>
      ))}
    </section>
  );
}