# Selected Provider Evidence Staleness Contract V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

- Provider context fixtures or older rows may omit holdings / exposure rows.
- More conservative selected monitoring policy can increase `NEEDS_INPUT` states compared with the older display-only interpretation.
- Provider data may need separate ingestion runs, but dashboard must not trigger those runs directly.

## Mitigation

- Missing required provider areas are explicit `NEEDS_INPUT` rows.
- Stale and partial evidence are visible through row status and `Policy Reason`.
- The execution boundary remains read-only and disables provider collection, monitoring log auto write, approval, order, and auto rebalance.
