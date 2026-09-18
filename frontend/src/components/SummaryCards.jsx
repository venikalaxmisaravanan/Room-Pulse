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
 * The values are em dashes, not zeros: counting rooms would require room
 * records and the availability engine, and inventing numbers here would be
 * fake data. The cards exist so the layout and colour language are settled.
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
            title="No room data source yet"
            aria-label={`${card.label}: not available yet`}
          >
            —
          </p>
          <p className="summary-card__hint">{card.hint}</p>
        </article>
      ))}
    </section>
  );
}