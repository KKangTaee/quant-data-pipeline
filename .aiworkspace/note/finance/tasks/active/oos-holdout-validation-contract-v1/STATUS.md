# OOS Holdout Validation Contract V1 Status

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Completed

- Added `build_oos_holdout_validation()` to `app/services/backtest_temporal_validation.py`.
- Practical Validation result now carries compact `oos_holdout_validation` evidence.
- Validation Efficacy Audit now reads `OOS holdout validation` evidence when present.
- Service contract tests cover passing aligned evidence, short-history `NEEDS_INPUT`, and proxy-only `REVIEW`.
- Phase 10 board and durable docs now point to `regime-split-validation-v1` as the next task.

## Next

Start `regime-split-validation-v1`.
