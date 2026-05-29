# Construction Risk Source Map V1 Plan

Status: Complete
Created: 2026-05-29

## Goal

Phase 11 implementation 전에 현재 프로젝트가 이미 갖고 있는 portfolio construction risk evidence를 source map으로 고정한다.

이걸 하는 이유?

- concentration, overlap, correlation, risk contribution, component role / weight discipline을 새 저장 기능 없이 어디서 읽을 수 있는지 확인한다.
- 이미 있는 Practical Validation / Look-through Board / Robustness Lab / Final Review gate evidence를 중복 구현하지 않는다.
- 다음 구현이 DB-backed data collection인지, compact read model 정렬인지, gate policy 연결인지 구분한다.

## Scope

- 현재 Practical Validation diagnostics의 construction risk 관련 domain 확인
- provider holdings / exposure look-through board 확인
- Robustness Lab sensitivity, drop-one, weight tilt evidence 확인
- component return correlation / risk contribution proxy 확인
- Final Review gate policy group ownership 확인
- Phase 11 task order 재확정

## Out Of Scope

- 새 JSONL registry
- user memo / preset / comment storage
- raw holdings row, raw provider response, full covariance / return matrix artifact 저장
- broker order, live approval, auto rebalance
- UI polish 또는 화면 재배치
- 신규 DB collector 구현

## Completion Criteria

- `SOURCE_MAP.md`에 current evidence source, gap, recommended next implementation order를 정리한다.
- Phase 11 board에서 11-1을 complete로 표시하고 11-2를 next로 전환한다.
- ROADMAP / INDEX / root handoff log가 다음 작업을 `concentration-overlap-exposure-contract-v1`로 가리킨다.
- 문서 검증과 diff hygiene 검증을 통과한다.
