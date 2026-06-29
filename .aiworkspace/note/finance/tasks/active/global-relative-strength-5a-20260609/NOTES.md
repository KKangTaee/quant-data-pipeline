# Global Relative Strength 5A Notes

## Initial Findings

- Current GRS runtime flow is `backtest_execution -> runtime/backtest.py -> finance/sample.py -> finance/strategy.py -> result_bundle`.
- `finance/sample.py` currently calls `.interval(interval)` before `GlobalRelativeStrengthStrategy(rebalance_interval=interval)`.
- `global_relative_strength_allocation` already tracks raw selected tickers, trend rejected tickers, cash, holdings, and total return, but does not expose enough cash / concentration diagnostics for user interpretation.
- `_apply_real_money_hardening` can estimate turnover from `End Ticker`, `End Balance`, `Next Ticker`, `Next Balance`, and `Cash`, so better GRS row semantics will improve cost evidence too.

## Implemented Findings

- GRS interval double-application risk was real for `interval > 1`: DB runtime reduced rows and strategy also skipped rebalances. 5A makes strategy cadence the single owner.
- `score_return_columns` now remains a first-class runtime input. `score_lookback_months` is derived only when needed, and all-zero score weights are rejected as input error.
- GRS cash proxy is still required when configured. Risky ETF data gaps can reach the strategy exclusion / warning path, but cash proxy and ticker benchmark prices remain blocking preflight requirements.
- Top-N concentration is now explicit in result rows and bundle metadata. High cash share, unfilled slots, and max position weight are readable without adding another UI panel.
- Existing Selection History was sufficient once compatibility aliases were added; no separate GRS evidence / log / workbench panel was needed.
