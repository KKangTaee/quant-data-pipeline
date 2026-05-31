# Data Provenance Coverage V1 Notes

Status: Complete
Created: 2026-05-28

## Initial Findings

- `finance/loaders/provider.py` already returns source, source_type, source_ref, coverage_status, as_of_date, collected_at for operability / holdings / exposure.
- `finance/loaders/macro.py` already returns source, source_type, source_mode, source_ref, coverage_status, collected_at, staleness_days, snapshot_status.
- `app/services/backtest_practical_validation_provider_context.py` currently summarizes coverage but does not expose a consistent area-level provenance / freshness contract.
- A DB schema change is not required for the first usable slice.

## Implementation Notes

- Provider context schema moved from `1` to `2`.
- The new `provenance` object is compact and intentionally does not carry raw holdings rows.
- ETF provider staleness uses a 45-day default threshold. Stale evidence becomes `REVIEW`, not `BLOCKED`, because issuer update cadence varies.
- Macro staleness remains based on `load_macro_snapshot()` and the existing 10-day Practical Validation default.
- Source mix and coverage status weights are target-weight based for ETF provider areas.
- Macro source mix is series-count based because macro series are not portfolio components.
