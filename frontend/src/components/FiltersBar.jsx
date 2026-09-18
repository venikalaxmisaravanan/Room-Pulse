/**
 * Building / room type / minimum capacity controls.
 *
 * They are disabled on purpose: there is no room catalogue to filter yet.
 * Wiring them to real data is the "Find Me a Room" stage, so instead of
 * pretending they work, they sit visibly inactive with a short explanation.
 */
export default function FiltersBar() {
  return (
    <section className="panel filters" aria-labelledby="filters-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="filters-heading">
          Narrow it down
        </h2>
        <p className="panel__note">
          Placeholders — these switch on once the room catalogue and
          availability engine are connected.
        </p>
      </div>

      <div className="filters__grid">
        <label className="field">
          <span className="field__label">Building</span>
          <select className="field__control" defaultValue="" disabled>
            <option value="">All buildings</option>
          </select>
        </label>

        <label className="field">
          <span className="field__label">Room type</span>
          <select className="field__control" defaultValue="" disabled>
            <option value="">Any type</option>
          </select>
        </label>

        <label className="field">
          <span className="field__label">Minimum capacity</span>
          <input
            className="field__control"
            type="number"
            min="0"
            step="5"
            placeholder="e.g. 30"
            disabled
          />
        </label>
      </div>
    </section>
  );
}