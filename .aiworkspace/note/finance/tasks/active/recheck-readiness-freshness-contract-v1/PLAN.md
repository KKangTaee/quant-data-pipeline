# Recheck Readiness / Freshness Contract V1 Plan

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Goal

Selected Portfolio Dashboard의 Performance Recheck 실행 전 조건을 하나의 read-only operations preflight contract로 고정한다.

이걸 하는 이유?

- readiness와 symbol freshness가 따로 보이면 replay contract는 준비됐지만 price DB가 stale / missing인 상태를 사용자가 놓칠 수 있다.
- Final Review V2 selected row가 canonical source인데 recheck가 Current Candidate Registry에만 의존하면 선정 이후 재검증이 불안정하다.
- 이 작업은 검증 효력 강화용 read model 정렬이며, user memo / preset / monitoring log 저장 기능을 만들지 않는다.

## Scope

- Final Review embedded replay contract와 Current Candidate Registry fallback을 함께 읽는 selected recheck contract resolver 추가
- readiness와 symbol freshness를 합친 `selected_recheck_operations_preflight_v1` runtime contract 추가
- Selected Portfolio Dashboard에 Recheck Operations Preflight 표시 추가
- stale / missing / blocked freshness와 replay contract gap이 pass처럼 보이지 않도록 service contract test 추가
- Phase 12 board, roadmap, root handoff log 동기화

## Out Of Scope

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset / comment persistence
- OHLCV 수집 실행
- provider / FRED direct UI fetch
- broker order, live approval, auto rebalance
- account holdings 자동 연결

## Completion Criteria

- Preflight route가 `READY / REVIEW / NEEDS_DATA / BLOCKED`로 readiness와 freshness를 함께 판정한다.
- Embedded final decision contract가 있으면 Current Candidate Registry 없이도 preflight readiness가 가능하다.
- Missing replay contract, stale / missing price, DB latest date error는 ready로 처리하지 않는다.
- Dashboard는 preflight를 read-only로 표시하고 기존 readiness / symbol freshness 상세를 유지한다.
- Focused contract tests, compile, full service contracts, boundary / hygiene checks가 통과한다.
