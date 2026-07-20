# Runs

Last Updated: 2026-07-20

## Planning Inspection

- `rg`로 market mover sector/group/market-cap 경계를 확인했다.
- `finance/loaders/fundamentals.py`의 `FUNDAMENTAL_COLUMNS`와 statement shadow loader를 확인했다.
- `finance/data/db/schema.py`에서 asset profile과 statement shadow schema를 확인했다.
- `finance/loaders/us_stock_turnaround.py`에서 PIT filing-ledger 기반 diluted EPS source를 확인했다.

## Implementation Verification

- baseline: `tests/test_service_contracts.py -k market_mover` → `126 passed`.
- new focused suites: `tests/test_overview_market_movers_read_models.py tests/test_overview_market_mover_research.py` → `16 passed`.
- relevant existing contracts: `tests/test_service_contracts.py -k market_mover` → `126 passed`.
- sector/group expanded contracts: `tests/test_service_contracts.py -k "market_mover or group_leadership"` → `129 passed` during Task 3.
- target `py_compile` → exit 0.
- full `tests/test_service_contracts.py` → `839 passed, 13 failed, 41 subtests passed`. 13 failures are existing out-of-scope Backtest Practical Validation / Final Review and Market Sentiment expectations; Market Movers focused suite has no failure.

## Real DB Read-Only Smoke

- SP500 / Top1000 / Top2000 × daily / weekly / monthly movers + sector group snapshot → all `OK`; readiness was `PARTIAL`, bellwether rows were 33 per snapshot.
- Top2000 industry daily / weekly / monthly, minimum group size 5, top 10 groups → `10` group rows and `30` bellwether rows per period.
- bounded current TTM PER sample AAPL/MSFT/NVDA/AMZN/GOOGL/META/LLY/AVGO/JPM/XOM → `0/10 READY`; 모두 `INCOMPLETE_REPORTED_DILUTED_EPS`였다.
