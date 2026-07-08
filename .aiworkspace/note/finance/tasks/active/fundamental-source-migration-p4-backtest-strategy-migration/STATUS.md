# Phase 4. Backtest Strategy Migration Status

## 2026-06-30

- Added catalog defaults: `DEFAULT_SINGLE_STRATEGY_OPTION=Quality + Value`, `DEFAULT_COMPARE_STRATEGY_OPTIONS=[Quality + Value, GTAA, Equal Weight]`.
- Reordered Single / Compare strategy options so statement annual factor family appears first.
- Updated Single Strategy selectbox to use the catalog default and clarify that new runs start from statement annual factors.
- Updated Portfolio Mix Builder default selection to strict annual factor bridge plus ETF sleeves.
- Reworded Broad vs Strict guide so `Quality Snapshot` is explicitly legacy broad yfinance compatibility, not a recommended quick path.
- Updated backtest UI / strategy architecture docs.

## Browser QA

- URL: `http://localhost:8525/backtest`
- Single Strategy default showed `Quality + Value`, variant `Strict Annual`, and rendered `Quality + Value Snapshot (Strict Annual)`.
- Portfolio Mix Builder default showed `Quality + Value`, `GTAA`, `Equal Weight`; `Quality + Value` variant was `Strict Annual`.
- Visible page had no `Traceback` or `ImportError`.
- Screenshot: `.aiworkspace/note/finance/run_artifacts/backtest_statement_annual_default_20260630.png`
