/**
 * Building / room type / minimum capacity requirements for current room search.
 */
export default function FiltersBar({
  filters,
  onChange,
  onFind,
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
          Find Me a Room
        </h2>
        <p className="panel__note">
          Search the latest RoomPulse snapshot for rooms that are currently
          usable.
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

      <button
        type="button"
        className="filters__find"
        onClick={onFind}
        disabled={disabled}
      >
        Find Rooms
      </button>

      {showReset && (
        <button
          type="button"
          className="filters__reset"
          onClick={onReset}
          disabled={disabled}
        >
          Clear filters
        </button>
      )}
    </section>
  );
}