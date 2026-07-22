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
- 현재 단계는 plan-only다. 제품 테스트와 Browser QA는 실행 방식 선택 후 수행한다.
