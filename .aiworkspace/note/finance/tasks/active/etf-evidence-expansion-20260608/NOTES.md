# Notes

Status: Completed
Last Verified: 2026-06-08

## Decisions

- 3D will not rerun ETF candidates or create current candidate registry rows.
- 3D will expose evidence gaps and next workflows as a read-only Backtest Analysis panel.
- GTAA / Equal Weight remain the first evidence-mature ETF sleeves; GRS / Risk Parity / Dual Momentum remain evidence-expansion targets.

## Context

- Research bundle says GRS has core/runtime/UI replay smoke but lacks current candidate hub.
- Risk Parity Trend and Dual Momentum are catalog-supported but lack durable report / current anchor depth.
- ETF strategies require provider operability, cost, benchmark, liquidity, concentration, and stale-data evidence before Final Review emphasis.

## Implementation Notes

- GRS is first priority because it has the strongest existing runtime / replay anchor among non-mature ETF strategies.
- Risk Parity Trend remains second because defensive allocation value is plausible, but low-vol overweight, volatility window, and correlation-regime evidence are not yet normalized.
- Dual Momentum remains third because top-1 concentration, whipsaw, cash proxy, and guardrail evidence need a stronger anchor before Practical Validation emphasis.
- The panel intentionally says candidate writes and backtest reruns are disabled.
