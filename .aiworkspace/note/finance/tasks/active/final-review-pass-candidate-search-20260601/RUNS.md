# Runs

- `git status --short`: pre-existing dirty generated/local files remain.
- Fresh dry-run sweep, no persistence:
  - `GRS Liquid Macro Top2`: 2016-01-29 to 2026-05-29, CAGR `0.1330973384`, MDD `-0.1774789654`, Sharpe `1.1221296315`, net spread `0.0718244521`, net cost curve `applied_with_measurable_cost`, turnover `estimated_from_holdings`, replay PASS, period coverage PASS, Practical Validation `READY_FOR_FINAL_REVIEW`, preflight `SELECTED_ROUTE_PREFLIGHT_READY`, Final Review packet `INVESTABILITY_PACKET_READY`, selected gate Ready.
  - `GTAA Default Top3`: 2016-03-31 to 2026-05-29, CAGR `0.0702987889`, MDD `-0.1888364703`, Sharpe `0.7231463440`, net spread `0.0128150826`, replay PASS, selected gate Ready.
  - `Risk Parity Trend Core`: replay PASS but Practical Validation `BLOCKED`; selected gate blocked by data trust / robustness.
  - `Dual Momentum Core`: replay PASS but Practical Validation `BLOCKED`; selected gate blocked by data trust / robustness.
  - `Equal Weight Dividend ETFs Regression`: replay PASS but selected gate not ready; missing turnover / net cost proof remains `REVIEW_REQUIRED` under Backtest Realism.
