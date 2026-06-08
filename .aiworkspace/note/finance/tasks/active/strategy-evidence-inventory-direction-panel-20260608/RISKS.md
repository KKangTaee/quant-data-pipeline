# Risks

Status: Active
Last Verified: 2026-06-08

## Mitigated During Task

- The strategy catalog may expose aliases / family variants differently than the research strategy names; focused tests now require every canonical catalog key to have an inventory row.
- Static maturity labels can drift from strategy catalog additions; the read model raises catalog coverage drift and tests cover special labels.
- UI placement must stay explanatory and read-only; Browser QA confirmed it appears as Backtest Analysis guidance, and no save / run / registry action was added.

## Residual Risks

- Maturity labels are static product interpretation and should be revisited when a strategy is materially reworked.
- The Direction Panel uses Streamlit dataframe rendering; the service tests, not DOM text extraction, are the strongest coverage for all row values.

## Deferred

- Risk-On Momentum Practical Validation / Final Review / Portfolio Monitoring governance.
- Strict quarterly prototype maturation.
- GRS / Risk Parity / Dual Momentum current-candidate evidence expansion.
- Strict annual + GTAA / Equal Weight bridge execution.
