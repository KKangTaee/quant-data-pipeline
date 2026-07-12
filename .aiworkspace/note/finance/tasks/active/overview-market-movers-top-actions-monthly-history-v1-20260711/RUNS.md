# Runs

- MySQL read-only: FDXF `2026-05-27~2026-07-10`, 31 daily rows; HONA `2026-07-10`, 1 daily row.
- Provider read-only `probe_ohlcv_provider(periods=("1y",))`: FDXF 31 rows, HONA 1 row, rate-limit/no-data 아님.
- Run history: 2026-07-11 17:12 Monthly smart refresh가 두 symbol을 성공 처리했으나 `insufficient_window_rows`가 그대로 남았다.
- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`: 146 tests passed.
- `npm run build` (`market_movers_workbench`): Vite production build passed.
- `py_compile`, `git diff --check`: passed.
- MySQL write: `market_data_issue(issue_type=limited_price_history)` FDXF/HONA 2 rows backfill.
- Live preflight: `status=limited`, selected 0, limited 2, FDXF/HONA.
- Browser QA: S&P 500 Monthly 선택, 짧은 이력 상태/간결 action/외부 설명/랭킹 렌더 확인. Screenshot `market-movers-monthly-top-actions-limited-history-qa.png`.
