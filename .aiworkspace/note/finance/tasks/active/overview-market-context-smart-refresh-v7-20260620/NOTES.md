# Notes

## User Problem

- `이벤트 배경: 직접 원인 근거 약함`은 실제 시장맥락 도출 기능이 아니라 calendar/source caveat에 가깝다.
- `필요 자료 일괄 보강`은 현재 이슈와 관계없이 7개 jobs를 모두 실행해 느리고, 어떤 이슈가 해결되는지 불명확하다.
- 보강할 수 없는 이벤트 성격 제한과 실제로 갱신 가능한 stale/missing data가 같은 UX 안에 섞여 있다.

## Decision

- Top brief should keep only actual market-context conclusion rows: movement, breadth, Futures/Macro.
- Events remain in timeline/source evidence unless a separate future design makes them a real cause-analysis dimension.
- Default refresh should run only actionable current issues.
- Full refresh remains available as secondary fallback.

## Implemented Model

- `refresh_plan.items`: 실행 대상. Examples: `sp500_intraday_snapshot`, `futures_1m`, `earnings_calendar`.
- `refresh_plan.excluded_items`: 수집으로 해결되지 않는 제한. Events estimate caveat is listed here instead of being rendered as a brief conclusion.
- `resolution`: `resolvable`, `partial`, or `not_actionable`.
- `Earnings Calendar` is `partial` because provider-estimated schedules can remain weak direct-cause evidence after refresh.
