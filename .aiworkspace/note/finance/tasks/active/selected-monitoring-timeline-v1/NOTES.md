# Selected Monitoring Timeline V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- Selected Dashboard already has Performance Recheck, Review Signals, Actual Allocation drift, and alert preview helpers.
- The missing piece is an ordered timeline that explains which signal came from selection, recheck, drift, or stored Final Review trigger.
- Existing `Update Review Signals` stores only session state, not a registry row.

## Implementation Notes

- Timeline rows are fixed and source-labeled: Final Review selection, evidence gate snapshot, Performance Recheck, Actual Allocation drift, Review trigger preview.
- Missing Performance Recheck is `NEEDS_INPUT`, not pass.
- Actual Allocation and alert preview remain optional unless the user has entered session state for them.
- `execution_boundary.monitoring_log_auto_write` is `False`; timeline generation does not append `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`.
- UI keeps Review Signals as the detailed trigger board and uses Timeline for ordered status context.
