# Backtest Practical Validation Handoff Gate V1 Notes

## Decisions

- The handoff button means "move this Backtest result to second-stage Practical Validation."
- The button should be enabled only when first-stage candidate readiness has no blocker.
- `can_move_to_compare` remains the source of truth because it already requires Promotion not hold, no execution source blocker, and no validation source blocker.
- A disabled button should explain the first blockers instead of silently doing nothing.
