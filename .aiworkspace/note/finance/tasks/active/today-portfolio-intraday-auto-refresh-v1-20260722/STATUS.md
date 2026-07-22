# Today Portfolio Intraday Auto Refresh V1 Status

Status: 1/4 In Progress — Task 1 Complete
Roadmap: 0/4 implementation stages complete
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

## Next

- 1/4차 Task 2 group scope, confirmed-session gate, DB due-check와 advisory lock을 TDD로 구현한다.
- 기존 AAII baseline 오류 2개는 사용자 승인에 따라 이번 Today scope와 분리한다.
