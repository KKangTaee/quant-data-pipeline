# Phase 11 Board Open Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 10이 walk-forward / OOS / regime validation efficacy를 완료했으므로, 다음 약점인 portfolio construction risk controls를 별도 phase로 열어야 한다.
코드 구현을 바로 시작하기 전에 concentration, overlap, correlation, risk contribution, role / weight discipline의 목적과 저장 경계, task 순서를 명확히 고정한다.

## Scope

포함한다.

- Phase 11 active board 생성
- Phase 11 task board와 immediate next task 정의
- Roadmap / root handoff log sync
- Phase 10 closeout handoff 반영

포함하지 않는다.

- runtime construction risk logic 변경
- 새 DB schema
- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- paid data source 도입

## Done Criteria

- Phase 11 active phase docs가 생성된다.
- `construction-risk-source-map-v1`이 다음 task로 명확히 남는다.
- Roadmap이 Phase 11 active 상태를 가리킨다.
- 저장 경계가 Phase 11 문서에 명확히 남는다.
- `git diff --check`가 통과한다.
