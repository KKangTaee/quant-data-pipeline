# Runtime Backtest Risk-On Momentum Split Notes

## Decisions

- 8차는 full runtime rewrite가 아니라 `app/runtime/backtest.py` compatibility facade split으로 진행한다.
- First slice is Risk-On Momentum 5D because it has a clear strategy-family boundary and dedicated finance modules.
- Shared freshness helper remains in `app/runtime/backtest.py` for now to avoid mixing 8A with a broader helper extraction.

## Observations

- `app/runtime/backtest.py` still remains large after 8A because ETF family, strict annual / quarterly family, and real-money contract helpers are still inside it.
- The split removes direct `finance.swing` / `finance.swing_analysis` imports from `app/runtime/backtest.py`.
- Existing `app/services/backtest_execution.py`, `app/services/backtest_compare_catalog.py`, and `app/runtime/__init__.py` can continue importing from `app.runtime.backtest`.
