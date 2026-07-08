# Status

## 2026-06-30

- Updated `app/web/ingestion_console.py` so broad yfinance fundamentals / factor jobs are archived compatibility jobs in `JOB_GUIDE`, not active UI cards.
- Removed the active `Legacy broad yfinance fundamentals / factors`, `핵심 시장 데이터 일괄 수집`, `펀더멘털 수동 수집`, and `팩터 수동 계산` expanders.
- Kept `weekly_fundamental_refresh`, `collect_fundamentals`, `calculate_factors`, and `pipeline_core_market_data` action handlers for saved/history replay compatibility.
- Updated `app/web/backtest_single_forms.py` so broad `Quality Snapshot` is clearly archived for saved/history replay, with strict annual alternatives named for new runs.
- Added contract tests that prevent reintroducing active broad yfinance financial statement cards while preserving compatibility handlers.
