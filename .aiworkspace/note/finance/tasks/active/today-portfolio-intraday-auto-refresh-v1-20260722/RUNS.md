# Today Portfolio Intraday Auto Refresh V1 Runs

## 2026-07-22 Design Investigation

- finance INDEX / ROADMAP / PROJECT_MAP / data docs와 Today·Portfolio Monitoring recent task를 확인했다.
- `market_intraday_snapshot` schema와 quote-fast collector/UPSERT를 확인했다.
- Market Movers의 `st.fragment(run_every=300)` browser auto-refresh flow를 확인했다.
- Today React가 stable component event/payload bridge를 사용하고 현재 EOD curve를 `stored_close`, `intraday=false`로 명시하는 것을 확인했다.
- Portfolio Monitoring의 direct stock·ETF EOD refresh와 latest-completed-session 검증을 확인했다.

## Verification

- `superpowers:writing-plans` 절차로 승인 설계를 9개 TDD task와 4개 roadmap stage로 분해했다.
- plan self-review에서 spec coverage, placeholder, type/status consistency를 대조했다.
- `git diff --check`를 통과했다.
- 이 기록 시점에는 plan-only였으며, 이후 사용자가 Inline Execution을 선택했다.

## 2026-07-23 Task 1 — Explicit Symbol Collector

- baseline `MarketIntelligenceIngestionContractTests`: 21개 중 Today와 무관한 기존 AAII parser/header 2개 오류. 사용자 승인으로 별도 이슈로 유지했다.
- RED: explicit collector 테스트 2개가 missing function으로 실패하는 것을 확인했다.
- GREEN: explicit group symbol 저장과 batch exception error-row 저장 테스트 2개 통과.
- 회귀: 기존 S&P 500/TOP1000/default liquidity/active alias/alias UPSERT 테스트 5개 통과.
- `.venv/bin/python -m py_compile finance/data/market_intelligence.py`와 `git diff --check` 통과.
