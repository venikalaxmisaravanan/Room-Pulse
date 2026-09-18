import { EMPTY_FILTERS } from "../utils/roomFilters.js";

/**
 * Building / room type / minimum capacity filters.
 *
 * These now work: they filter the room catalogue that is already loaded in the
 * browser, so no extra backend query is needed. They stay disabled until the
 * catalogue arrives, because there would be nothing to choose from.
 *
 * Availability is still not part of the query — "find me a room that is free
 * right now" needs the availability engine, which is a later stage.
 */
export default function FiltersBar({
  filters,
  onChange,
  options,
  disabled,
  onReset,
  showReset,
}) {
  const setField = (field) => (event) =>
    onChange({ ...filters, [field]: event.target.value });

  return (
    <section className="panel filters" aria-labelledby="filters-heading">
      <div className="panel__head">
        <h2 className="panel__title" id="filters-heading">
          Narrow it down
        </h2>
        <p className="panel__note">
          Filters the loaded catalogue in your browser. Availability-aware
          search arrives with the availability engine.
        </p>
      </div>

      <div className="filters__grid">
        <label className="field">
          <span className="field__label">Building</span>
          <select
            className="field__control"
            value={filters.building}
            onChange={setField("building")}
            disabled={disabled}
          >
            <option value="">All buildings</option>
            {options.buildings.map((building) => (
              <option key={building} value={building}>
                {building}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span className="field__label">Room type</span>
          <select
            className="field__control"
            value={filters.roomType}
            onChange={setField("roomType")}
            disabled={disabled}
          >
            <option value="">Any type</option>
            {options.roomTypes.map((roomType) => (
              <option key={roomType} value={roomType}>
                {roomType}
              </option>
            ))}
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
            value={filters.minCapacity}
            onChange={setField("minCapacity")}
            disabled={disabled}
          />
        </label>
      </div>

      {showReset && (
        <button
          type="button"
          className="filters__reset"
          onClick={() => onChange(EMPTY_FILTERS)}
          disabled={disabled}
        >
          Clear filters
        </button>
      )}
    </section>
  );
}