# Notes

## User Problem

- `현재 이슈만 보강` excludes Events, but `근거: 자료 기준 / 출처 상태` still shows Events as `자료 확인 필요`.
- Data Health is a meta read model, not a market-context source, but it also appears as an unresolved source issue.
- Top `자료 상태` says `일부 자료 확인 필요` without explaining which items are actually actionable.

## Decision

- Actionable stale/missing source issues should drive the top `자료 상태`.
- Events estimate limitations are reference caveats unless future cause-analysis logic is approved.
- Data Health should be management/meta evidence. It can explain where actionable items came from, but it should not count as an unresolved Market Context source issue.
