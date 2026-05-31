# Design

## Candidate Families

- Equal Weight ETF mixes
- Risk Parity Trend
- Dual Momentum
- Global Relative Strength
- strict Quality / Value / Quality+Value factor snapshots if the DB factor coverage is sufficient

## Execution Approach

1. Run non-GTAA strategies through the same compare runtime used by Backtest Analysis.
2. Build temporary Clean V2 selection sources from strategy bundles or weighted mix bundles without persisting them.
3. Run Practical Validation with latest replay evidence where supported.
4. Evaluate Final Review evidence packet and selected-route gate.
5. Persist only a candidate whose selected-route gate allows selection.

## Safety

- Dry-run candidates are in memory only.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` is append-only and used only after the selected-route gate passes.
- Dashboard confirmation is read-only.
