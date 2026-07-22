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

## 2026-07-23 Task 2 — Scope, Session, Due, Lock

- RED: 신규 intraday service module 부재로 focused 테스트 9개가 실패하는 것을 확인했다.
- GREEN: group scope/hash, direct-security eligibility, OPEN gate, pre-open/close, 300초 due, 600초 stale, partial coverage, lock contention/release, DB restart cadence 테스트 9개 통과.
- 회귀: 신규 service와 기존 Portfolio Monitoring EOD refresh를 합친 17개 테스트 통과.
- `py_compile` 대상 3개와 `git diff --check` 통과.

## 2026-07-23 Task 3 — Non-Blocking Coordinator

- RED: Today coordinator module 부재로 focused 테스트 5개가 실패하는 것을 확인했다.
- GREEN: due OPEN submit, non-blocking result, one-inflight, not-due skip, closed/limited skip, completed future 수거 테스트 5개 통과.
- 회귀: coordinator + Today market session + intraday scope 14개 테스트 통과.
- `py_compile app/web/today_intraday_auto_refresh.py`와 `git diff --check` 통과.

## 2026-07-23 Task 4 — Fragment And Default Context

- RED: read-only context loader, 15초 fragment, dynamic body가 없어 focused 테스트 3개가 실패하는 것을 확인했다.
- GREEN: default group/items/workspace read, stable key, heartbeat tick 테스트 3개 통과.
- 회귀: coordinator, Today page contract, market session, intraday service를 합친 39개 테스트 통과.
- Today public page의 bare-test 경로와 실제 Streamlit fragment 경로를 분리해 기존 navigation/fallback 계약을 보존했다.
- `py_compile` 대상 3개와 `git diff --check` 통과.

## 2026-07-23 Task 5 — DB-Backed Live Valuation

- RED: live overlay와 EOD close loader 부재로 focused 테스트 5개가 import error로 실패하는 것을 확인했다.
- GREEN: fixed-notional, fixed-shares retained cash, selected-strategy EOD 유지, partial/all-failed, Modified Dietz flow, basis-date EOD close 테스트 5개 통과.
- 회귀: intraday service, 기존 valuation, position-event ledger를 합친 41개 테스트 통과.

## 2026-07-23 Task 6 — Today Live Read Model

- RED: `portfolio_live` 인자와 `portfolio.live` 계약 부재로 focused 테스트 2개가 실패하는 것을 확인했다.
- GREEN: `today_home_v4`, READY/INACTIVE allowlist, EOD curve 불변, provider diagnostics 비노출 테스트 통과.
- 회귀: Today read-model/page/coordinator/session/navigation 49개 테스트 통과.

## 2026-07-23 Task 7 — React Live Overlay

- RED: live selector 부재로 Vitest 3개가 실패하는 것을 확인했다.
- GREEN: live/EOD fallback/partial coverage presentation을 포함한 Vitest 13개 통과.
- TypeScript typecheck와 Vite production build 통과, static bundle 재생성.
- Python Today read-model/static component 계약 18개 통과.
