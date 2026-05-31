# Cost / Slippage Sensitivity Audit V1 Risks

| Risk | Mitigation |
| --- | --- |
| Generic robustness sensitivity is mistaken for cost / slippage sensitivity | Require explicit cost / slippage wording or contract fields for PASS |
| Missing sensitivity is hidden by strong cost / liquidity evidence | Add a separate audit row after net cost curve / turnover evidence |
| New persistence creeps back into the workflow | Keep task read-only and verify no registry / saved / artifact writes are added |
| Existing ready fixture becomes weaker than production expectations | Update test fixture with explicit compact sensitivity evidence |

## Residual Risk

- This task audits the presence and quality of sensitivity evidence. It does not yet implement a new runtime cost bps sweep or market impact simulator.
- The next Phase 9 task should verify that selected-route gate policy treats `BACKTEST_REALISM_REVIEW` and `BACKTEST_REALISM_NEEDS_INPUT` sensitivity gaps with the intended severity.
