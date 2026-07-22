# Today Portfolio Intraday Auto Refresh V1 Status

Status: 2/4 Complete
Roadmap: 2/4 implementation stages complete
Last Updated: 2026-07-23

## Completed

- Today EOD portfolio projection과 market-session V1 계약을 확인했다.
- 기존 `market_intraday_snapshot`, quote-fast collector, UPSERT와 Market Movers 5분 fragment pattern을 확인했다.
- 기존 Portfolio Monitoring EOD refresh와 `latest_completed_nyse_session` close handoff 경계를 확인했다.
- 사용자가 자동 background refresh, graph·return update와 5분 cadence를 승인했다.
- no-loading live overlay와 close handoff 설계를 `DESIGN.md`에 작성했다.
- 사용자가 written spec을 승인했다.
- `IMPLEMENTATION_PLAN.md`에 1/4차~4/4차를 9개 TDD task로 분해했다.
- Task 1 explicit-symbol collector를 TDD로 구현했다.
- 최대 10개 `TODAY_<group hash>` symbol과 UTC minute replay key를 고정했다.
- provider batch exception도 symbol별 `provider_status=error` row로 저장한다.
- Task 2 group SHA-256 scope, direct stock·ETF eligibility, confirmed regular-session gate를 구현했다.
- DB latest attempt 300초 cadence, quote 600초 stale, partial coverage와 MySQL advisory lock을 구현했다.
- 새 process에서도 DB attempt가 cadence source-of-truth가 되는 회귀를 확인했다.
- Task 3 process-cached single-worker coordinator를 구현했다.
- main thread에서 due state만 확인하고 running future의 `result()`를 호출하지 않으며 group별 one-inflight를 유지한다.
- Task 4 read-only default group context와 `st.fragment(run_every=15)` heartbeat를 Today에 연결했다.
- stable `today_workbench` component key, 기존 fallback/navigation, EOD-only interim render를 보존했다.
- Task 5 DB-backed live valuation을 구현했다.
- direct stock·ETF는 보유 수량과 EOD retained cash를 보존해 live value를 계산하고, selected strategy는 EOD value를 유지한다.
- fresh/partial/all-failed coverage, EOD close basis-date 조회, Modified Dietz 장중 수익률을 41개 회귀로 확인했다.
- Task 6 `today_home_v4`의 allowlisted `portfolio.live` 계약을 추가했다.
- Today heartbeat가 DB snapshot과 workspace EOD close만 읽어 live overlay를 연결하며 historical curve/metrics는 바꾸지 않는다.

## Next

- 3/4차 Task 7 React metrics와 dashed live point를 연결한다.
- 기존 AAII baseline 오류 2개는 사용자 승인에 따라 이번 Today scope와 분리한다.
