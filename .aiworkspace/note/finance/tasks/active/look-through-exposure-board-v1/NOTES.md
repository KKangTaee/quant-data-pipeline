# Look-through Exposure Board V1 Notes

Status: Complete
Created: 2026-05-28

## Initial Findings

- `finance/loaders/provider.py` already returns normalized holdings / exposure snapshots with source, source_type, coverage_status, as_of_date, and collected_at.
- `app/services/backtest_practical_validation_provider_context.py` already builds compact holdings and exposure diagnostics.
- Current UI shows Provider Coverage rows and Provider Data Gaps, but not a dedicated holdings / exposure board.
- Final Review currently repeats Provider Coverage but lacks an explicit look-through summary.

## Design Notes

- Board should reuse provider context instead of fetching DB data in UI.
- Board rows should stay compact and table-friendly.
- Full holdings rows must remain DB-only.
- The board is intentionally nested under `provider_coverage.look_through_board`; top-level duplication in validation / final decision rows was avoided.
