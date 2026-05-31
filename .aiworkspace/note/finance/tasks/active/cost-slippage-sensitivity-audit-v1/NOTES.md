# Cost / Slippage Sensitivity Audit V1 Notes

## Findings

- `robustness_lab_board_v1` already summarizes generic sensitivity coverage and runtime follow-up, but its default checks are window / drop-one / weight tilt oriented.
- Backtest Realism Audit currently reads cost application, net cost curve, turnover, liquidity, net policy, rebalance, tax/account, and execution boundary.
- The missing boundary is whether sensitivity evidence specifically covers cost / slippage assumptions.

## Implementation Boundary

- Add a compact read-only contract to `app/services/backtest_realism_audit.py`.
- Reuse existing validation payload fields; do not add persistence or fetch providers from UI.

## Result

- Backtest Realism Audit now exposes `cost_slippage_sensitivity_contract`.
- Strong PASS requires explicit cost / slippage sensitivity evidence.
- Generic robustness sensitivity is visible but insufficient for cost / slippage PASS.
- Missing sensitivity no longer hides behind strong transaction cost / net curve / liquidity evidence.
