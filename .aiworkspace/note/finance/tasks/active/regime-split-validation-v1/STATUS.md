# Regime Split Validation V1 Status

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Completed

- Added `build_regime_split_validation()` to `app/services/backtest_temporal_validation.py`.
- Practical Validation now reads DB-backed macro history through `finance.loaders.macro.load_macro_series_observations()`.
- Practical Validation result now carries compact `regime_split_validation` evidence.
- Validation Efficacy Audit now reads `Regime split validation` evidence when present.
- Service contract tests cover passing official macro evidence, missing macro `NEEDS_INPUT`, and proxy macro `REVIEW`.
- Phase 10 board and durable docs now point to `validation-efficacy-gate-policy-refinement-v2` as the next task.

## Next

Start `validation-efficacy-gate-policy-refinement-v2`.
