# Status

Status: Completed
Last Updated: 2026-06-20

## Summary

`Overview > Market Context` V7 보정 작업이다. Events를 상단 시장 브리프에서 낮추고, 필요 자료 보강을 전체 일괄 실행이 아니라 현재 이슈 기반 smart refresh로 바꾼다.

## Completed

- `오늘의 시장 브리프`는 움직임, 확산/집중, Futures/Macro 배경 3행으로 정리했다.
- Events는 기본 브리프에서 제거하고 event timeline / source evidence / context finding에만 남겼다.
- `refresh_plan` read model을 추가해 보강 가능 / 일부 보강 / 보강 제외 항목을 분리했다.
- 기본 refresh button은 `현재 이슈만 보강`으로 바꿔 `refresh_plan.action_ids`만 실행한다.
- 기존 7개 job 전체 실행은 `전체 Market Context 자료 보강` fallback으로 유지했다.
- refresh 실행 결과는 raw job rows 전에 브리프 반영 요약을 먼저 보여준다.
- Futures/Macro stale limitation row는 Futures Monitor / Data Health source/freshness metadata로 고정했다.

## Pending

- none.

## Boundary

- 새 provider, DB schema, loader, registry/saved JSONL write는 만들지 않는다.
- UI render 중 provider 직접 fetch는 하지 않는다.
- Events / sentiment / FRED hard conditioning이나 trade signal / recommendation / validation / monitoring semantics는 추가하지 않는다.
