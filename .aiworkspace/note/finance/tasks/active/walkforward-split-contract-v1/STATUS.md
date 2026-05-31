# Walk-forward Split Contract V1 Status

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Completed

- Added `app/services/backtest_temporal_validation.py`.
- Added benchmark-aligned walk-forward rows for:
  - computed windows
  - worst rolling excess return
  - negative excess window share
  - worst drawdown gap
  - curve source strength
- Practical Validation result now carries compact `temporal_validation` evidence.
- Validation Efficacy Audit now reads temporal validation evidence when present.
- Service contract tests cover passing aligned evidence, short-history `NEEDS_INPUT`, and proxy-only `REVIEW`.

## Next

Start `oos-holdout-validation-contract-v1`.

Recommended scope:

- Reuse the temporal validation helper patterns.
- Build explicit in-sample / out-sample compact rows.
- Mark insufficient split history as `NEEDS_INPUT` or `REVIEW`.
- Keep raw split artifacts out of workflow JSONL.
