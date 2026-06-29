# Backtest Analysis Direction Reset 4C Notes

## User Direction

- This branch should improve backtest strategies, mature prototypes, and support new strategy development.
- Backtest Analysis should not keep accumulating evidence/log/readiness panels as the default experience.
- New explanation/body copy should be Korean-first. English titles are acceptable when useful.

## Implementation Notes

- Keep existing evidence panel services available to avoid losing work.
- Demote their UI placement instead of deleting them in this pass.
- Use tests to lock the default hidden policy before changing the Streamlit layout.
