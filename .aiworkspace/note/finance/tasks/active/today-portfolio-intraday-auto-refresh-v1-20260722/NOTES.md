# Today Portfolio Intraday Auto Refresh V1 Notes

## Decisions

- provider cadence는 5분이다.
- automatic refresh는 toggle 없이 Today 화면-open + confirmed regular-session OPEN에서만 동작한다.
- 15초 fragment heartbeat는 DB/future 상태만 확인하며 provider cadence를 바꾸지 않는다.
- UI는 provider를 직접 호출하지 않는다.
- intraday snapshot은 DB에 저장하지만 EOD daily-close table과 curve에는 넣지 않는다.
- live value, return, contribution과 chart point는 모두 `장중 임시` 의미다.
- close 후 confirmed daily row가 들어오면 live overlay를 제거한다.
- selected strategy는 live quote 대상이 아니다.
- 사용자가 written spec을 승인했으며 구현은 `IMPLEMENTATION_PLAN.md`의 9개 TDD task를 따른다.

## Existing Reuse

- `market_intraday_snapshot`
- `collect_and_store_market_intraday_snapshot`의 quote-fast normalization
- `upsert_intraday_snapshot_rows`
- Market Movers `st.fragment(run_every=300)` browser-open pattern
- Portfolio Monitoring `run_portfolio_price_refresh`
- Today `market_session` official calendar schedule
- Portfolio Monitoring position ledger / Modified Dietz valuation

## Plan Boundaries

- 1/4차: explicit symbol collection, group scope, DB due/lock
- 2/4차: single-worker coordinator와 15초 fragment
- 3/4차: Python live valuation과 React overlay
- 4/4차: EOD handoff, 회귀, actual Browser QA, durable docs
