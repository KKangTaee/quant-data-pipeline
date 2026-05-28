# Symbol Lifecycle Event Fields V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- Existing DB tables will receive nullable columns through `sync_table_schema`; enum changes to existing columns are not required.
- Event fields must not loosen Data Coverage Audit PASS criteria.
- The task should not create another persistence surface outside DB.

## Remaining Gaps

- Phase 8 still needs a historical membership / ticker action source review.
- Form 25 remains delisting evidence only and does not prove first listing date or complete membership.
