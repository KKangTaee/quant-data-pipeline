# Regime Split Validation V1 Risks

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Risks

- Regime bucket labels are simple threshold buckets, not a full macro model.
- The helper depends on stored FRED macro history; if ingestion has only current snapshots, historical split remains `NEEDS_INPUT`.
- Bucket sample size can be sparse in calm periods, so missing caution / risk-off months should not be read as strategy robustness.
- Gate policy still needs a later refinement pass to decide how temporal / OOS / regime gaps influence selected-route eligibility.
