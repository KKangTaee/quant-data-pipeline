# Runs

## 2026-06-08

| Time KST | Command / Action | Result |
|---|---|---|
| 10:29 | docs read order and workflow boundary review | In progress |
| 10:40 | Compare catalog full strategy exploration | Ran Equal Weight, GTAA presets, GRS, Risk Parity, Dual Momentum, Risk-On Momentum 5D, strict quality/value/Q+V variants. Strict/factor candidates had high CAGR but failed current workflow-complete Practical Validation replay requirement. |
| 10:55 | All-ETF weighted search | Selected GTAA U5 20% / GTAA U3 75% / GRS Compact 5% as workflow-complete candidate: CAGR 13.90%, MDD -13.44%, Sharpe 1.16 over 2016-08-31 to 2026-02-28. |
| 11:08 | Practical Validation dry run | Runtime replay PASS, validation route `READY_FOR_FINAL_REVIEW`, but initial Final Review gate blocked on missing Backtest Realism net-cost proof metadata. |
| 11:18 | Backtest Realism root cause check | Found component runtime meta already had `cost_application_status=applied_to_result_curve`, net cost curve, turnover evidence, and transaction cost bps. Weighted source needed those fields propagated into the Practical Validation source contract. |
| 11:25 | Practical Validation dry run with cost / turnover / net-curve contract | Final Review gate `READY_WITH_REVIEW`, selected-route preflight `SELECTED_ROUTE_PREFLIGHT_READY`, `NOT_RUN` critical domains 0. Cost-bps sensitivity passed for 0 / 10 / 20 / 30 bps. |
| 11:34 | Persist workflow chain | Persisted selection source, Practical Validation result, Final Review decision, and Portfolio Monitoring saved setup. |
| 11:35 | Portfolio Monitoring dry-run recheck | Performance recheck status `ok`, verdict `SELECTION_THESIS_HOLDS`, portfolio CAGR 13.88%, MDD -13.37%, SPY CAGR 12.87%, SPY MDD -24.80%. |
| 11:42 | `git diff --check` | PASS |
| 11:42 | `py_compile` focused workflow modules | PASS |
| 11:43 | dashboard state lookup | Portfolio dashboard status `Ready`, strategy count 1, missing strategy count 0, complete slot count 1, operation status `normal`. |
