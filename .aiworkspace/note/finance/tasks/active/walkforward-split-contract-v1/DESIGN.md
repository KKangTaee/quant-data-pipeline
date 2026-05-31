# Walk-forward Split Contract V1 Design

Status: Complete
Created: 2026-05-29

## Implemented Contract

New helper:

- `app/services/backtest_temporal_validation.py`
- schema: `walkforward_validation_contract_v1`
- public function: `build_walkforward_validation()`

Inputs:

- normalized or normalizable portfolio curve
- normalized or normalizable benchmark curve
- portfolio / benchmark curve source labels
- benchmark parity status
- rolling window length

Output:

- `status`: `PASS`, `REVIEW`, `NEEDS_INPUT`, or `BLOCKED`
- compact audit rows
- metrics including window count, common months, worst rolling excess return, negative excess window share, worst drawdown gap, and source strength
- storage boundary flags: no DB write, no registry write, no memo persistence

## Semantics

| Case | Result |
| --- | --- |
| Missing portfolio curve | `NEEDS_INPUT` |
| Missing benchmark curve | `NEEDS_INPUT` |
| Too few common months | `NEEDS_INPUT` |
| Benchmark parity not `PASS` | `REVIEW` |
| Proxy-only curve source | `REVIEW` |
| Weak worst rolling excess / drawdown gap | `REVIEW` |
| Enough aligned evidence with no review trigger | `PASS` |

## Integration

- Practical Validation diagnostics builds `temporal_validation` from existing portfolio / benchmark curves.
- `curve_evidence.temporal_validation` also carries the compact evidence for downstream readers.
- Validation Efficacy Audit adds `Walk-forward temporal validation` when the evidence exists.
- Final Review gate sees the impact through the existing Validation Efficacy Audit route and packet check.

## Storage Boundary

This is a read-only contract.
It does not write a new DB table, does not create a new JSONL registry, and does not persist user comments or presets.
