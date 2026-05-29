# Phase 8 Integrated QA Closeout Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8은 lifecycle / survivorship / historical membership evidence 약점을 DB-backed로 보강한 phase다.
구현 slice가 여러 개로 나뉘었기 때문에, 마지막 단계에서는 새 기능을 추가하기보다 전체 경로가 함께 안전하게 작동하는지 확인하고 다음 Phase 9로 넘길 handoff를 정리해야 한다.

## Scope

포함한다.

- Phase 8 task 완료 상태 확인
- lifecycle evidence source semantics 통합 검토
- compile / service contract / diff check 실행
- storage boundary 재확인
- Phase 8 closeout summary 작성
- Roadmap / phase board / root handoff log 정리

포함하지 않는다.

- 새 collector 또는 DB schema 추가
- 새 JSONL registry
- user memo / preset persistence
- UI direct fetch
- live approval / broker order / auto rebalance
- Phase 9 cost / slippage 구현

## Done Criteria

- Phase 8 task board가 완료 상태로 정리된다.
- 통합 검증 명령이 통과하거나, 실패 시 명확한 residual risk로 남는다.
- Phase 8 closeout summary가 `phases/done/`에 남는다.
- Phase 9 handoff가 roadmap과 closeout summary에 명확히 기록된다.
