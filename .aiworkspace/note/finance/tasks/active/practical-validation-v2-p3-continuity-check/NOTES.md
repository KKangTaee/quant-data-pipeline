# Practical Validation V2 P3 Continuity Check Notes

Status: Active
Last Updated: 2026-05-28

## Decisions

- Continuity check is a read model, not persistence.
- `Performance Recheck not run` should be `NEEDS_INPUT`, not a hidden pass.
- Missing selected route or invalid component target is blocking.
- Missing review trigger or evidence packet is review / needs-input, not automatic selection failure for historical rows.
- The check must keep live approval, order instruction, auto rebalance, and monitoring auto-write disabled.

## Implementation Notes

- `build_selected_portfolio_continuity_check()` reads selected dashboard row, raw final decision row, and monitoring timeline.
- Dashboard shows continuity before the monitoring tabs so users see whether downstream monitoring is ready, needs input, or blocked.
- Continuity check can show `CONTINUITY_NEEDS_INPUT` when Performance Recheck has not run; this is expected after initial selection.
