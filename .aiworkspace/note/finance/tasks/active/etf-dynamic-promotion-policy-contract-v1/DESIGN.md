# Design

## Findings

- `_apply_real_money_hardening` already stores benchmark, net CAGR spread, liquidity, rolling underperformance, and drawdown promotion policy metadata when caller arguments are non-null.
- `run_equal_weight_backtest_from_db` accepts these policy arguments but ETF dynamic strategies only accept/pass ETF AUM and bid-ask policy arguments.
- `app/services/backtest_execution.py`, `app/services/backtest_practical_validation_replay.py`, and `app/services/backtest_compare_catalog.py` mirror the same missing dynamic ETF policy surface.
- Backtest Realism Audit correctly treats missing `promotion_min_net_cagr_spread` as incomplete net policy evidence. Final Review selected-route gate should remain unchanged.

## Implementation Direction

- Add a small shared ETF dynamic promotion default contract aligned to the existing strict promotion defaults.
- Extend GTAA / GRS / Risk Parity / Dual Momentum runtime signatures and `input_params` to include:
  - `promotion_min_benchmark_coverage`
  - `promotion_min_net_cagr_spread`
  - `promotion_min_liquidity_clean_coverage`
  - `promotion_max_underperformance_share`
  - `promotion_min_worst_rolling_excess_return`
  - `promotion_max_strategy_drawdown`
  - `promotion_max_drawdown_gap_vs_benchmark`
- Pass those values into `_apply_real_money_hardening`.
- Preserve the same fields through Single Strategy dispatch, Compare defaults/overrides, and Practical Validation replay.
- Avoid registry/saved migration. Fresh or replayed outputs get the richer contract naturally.
