# Phase 10 Board Open Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 9가 cost / slippage / liquidity realism을 완료했으므로, 다음 약점인 walk-forward / out-of-sample / regime split validation을 별도 phase로 열어야 한다.
코드 구현을 바로 시작하기 전에, 검증 목적과 저장 경계, task 순서를 명확히 고정한다.

## Scope

포함한다.

- Phase 10 active board 생성
- Phase 10 task board와 immediate next task 정의
- Roadmap / root handoff log sync
- Phase 9 closeout handoff 반영

포함하지 않는다.

- runtime split validation logic 변경
- 새 DB schema
- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- paid data source 도입

## Done Criteria

- Phase 10 active phase docs가 생성된다.
- `walkforward-oos-source-map-v1`이 다음 task로 명확히 남는다.
- Roadmap이 Phase 10 active 상태를 가리킨다.
- 저장 경계가 Phase 10 문서에 명확히 남는다.
- `git diff --check`가 통과한다.
