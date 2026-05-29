# Walk-forward Split Contract V1 Notes

Status: Complete
Created: 2026-05-29

## Findings

- Practical Validation already had enough normalized curve source data to calculate walk-forward rows without new data storage.
- Existing Robustness Lab rolling evidence remains useful but is portfolio-only; this task adds benchmark-relative walk-forward evidence separately.
- Validation Efficacy Audit is the right first gate integration point because Final Review already reads its route.

## Implementation Notes

- `build_walkforward_validation()` uses monthly last observations and aligns portfolio / benchmark by month.
- It calculates rolling window portfolio return, benchmark return, excess return, strategy MDD, benchmark MDD, and drawdown gap.
- It stores a limited `window_rows_preview` inside metrics, not a raw full artifact.
- Proxy sources and benchmark parity gaps downgrade the row to `REVIEW`.

## Storage Note

No new JSONL registry, memo storage, preset persistence, report artifact, approval, order, or auto rebalance path was added.
