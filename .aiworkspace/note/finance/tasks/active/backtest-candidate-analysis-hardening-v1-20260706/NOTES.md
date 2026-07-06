# Notes

- `app/web/backtest_single_strategy.py` renders `_render_last_run()` after the strategy form without checking whether `backtest_last_bundle.meta.strategy_key` still matches the selected strategy.
- `app/web/backtest_result_display.py` labels missing `price_freshness.status` as `자료 제한`.
- `app/services/backtest_handoff_readiness.py` currently treats empty status as pass through `_PASS_STATUSES`, causing a mismatch with Data Trust UI.
- Strict Quality / Value presets are loaded from `nyse_asset_profile` market-cap order when available, with static fallback. They are not official S&P latest membership presets.
- `app/services/backtest_price_refresh.py` already uses the existing OHLCV ingestion job and writes to `finance_price.nyse_price_history`; the missing piece is post-refresh stale-result state.
