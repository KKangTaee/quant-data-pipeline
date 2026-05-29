# Selected Monitoring Source Map V1 Plan

Status: Complete
Created: 2026-05-29

## Goal

Phase 12 implementation 전에 Selected Portfolio Dashboard가 이미 갖고 있는 monitoring / recheck evidence source를 source map으로 고정한다.

이걸 하는 이유?

- 선정 이후 상태 확인이 Final Review decision row, Current Candidate Registry, DB price loader, provider context, session-state recheck / drift input 중 어디에서 오는지 분리한다.
- 이미 구현된 readiness / freshness / provider / timeline / comparison read model을 중복 구현하지 않는다.
- 다음 구현이 새 저장 기능인지, DB-backed data 보강인지, read model / severity policy 정렬인지 구분한다.

## Scope

- Selected Portfolio Dashboard runtime source ownership 확인
- Final Review V2 decision row와 selected filter 확인
- Current Candidate Registry replay contract dependency 확인
- DB latest market date / price freshness / latest close read path 확인
- provider evidence / look-through board read path 확인
- session-state Performance Recheck / Actual Allocation / alert preview 경계 확인
- Review Signals / Recheck Comparison / Timeline policy split 확인
- Phase 12 task order 재확정

## Out Of Scope

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset / comment storage
- account holdings 자동 연결
- broker order, live approval, auto rebalance
- UI direct provider / FRED / broker fetch
- 신규 DB schema 또는 collector 구현

## Completion Criteria

- `SOURCE_MAP.md`에 current evidence source, gap, recommended next implementation order를 정리한다.
- Phase 12 board에서 12-1을 complete로 표시하고 12-2를 next로 전환한다.
- ROADMAP / INDEX / root handoff log가 다음 작업을 `recheck-readiness-freshness-contract-v1`로 가리킨다.
- 문서 검증과 diff hygiene 검증을 통과한다.
