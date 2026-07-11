# Institutional Portfolios Holding Chart Refresh V1 Status

Status: Completed
Started: 2026-07-12
Completed: 2026-07-12

## Progress

- 2026-07-12: 실제 DB에서 Berkshire 상위 holdings 대부분이 `holding_symbol` 없이 저장되어 있으나 `finance_price.nyse_price_history`에는 KO/BAC/CVX/OXY/GOOGL 등 가격 row가 있음을 확인했다.
- 2026-07-12: 원인은 가격 수집 부재만이 아니라 conservative CUSIP-symbol join과 일부 오염된 DB map 때문에 보유종목 -> ticker 해석이 끊긴 것이었다.
- 2026-07-12: service-level curated CUSIP seed와 issuer token guard를 추가해 DB를 mutate하지 않고 chart/read model만 보강했다.
- 2026-07-12: selected-security chart가 비면 React button이 Python `run_collect_ohlcv` action으로 가격 수집을 요청하도록 연결했다.
- 2026-07-12: Browser QA에서 KO 상세의 저장 가격 차트와 보유 기관 리스트가 표시되는 것을 확인했다.

## Current Verification

- `tests.test_institutional_portfolios`: passing.
- `py_compile`: passing for touched Python files.
- `npm run build`: passing for Institutional Portfolios workbench.
- `git diff --check`: passing.
