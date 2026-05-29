# Phase 12 Board Open Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 11이 portfolio construction risk controls를 완료했으므로, 다음 약점인 selected monitoring / recheck operations를 별도 phase로 열어야 한다.
코드 구현을 바로 시작하기 전에 Selected Portfolio Dashboard가 선정 이후 운영 판단에서 무엇을 책임지고, 어떤 저장 / 거래 경계를 넘지 않는지 명확히 고정한다.

## Scope

포함한다.

- Phase 12 active board 생성
- Phase 12 task board와 immediate next task 정의
- Roadmap / root handoff log sync
- Phase 11 closeout handoff 반영

포함하지 않는다.

- runtime selected monitoring logic 변경
- 새 DB schema
- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- account holdings 자동 연결
- broker order / live approval / auto rebalance
- UI direct provider / FRED / broker fetch

## Done Criteria

- Phase 12 active phase docs가 생성된다.
- `selected-monitoring-source-map-v1`이 다음 task로 명확히 남는다.
- Roadmap이 Phase 12 active 상태를 가리킨다.
- 저장 경계가 Phase 12 문서에 명확히 남는다.
- `git diff --check`가 통과한다.
