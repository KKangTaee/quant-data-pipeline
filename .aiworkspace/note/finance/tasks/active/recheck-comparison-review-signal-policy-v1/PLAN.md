# Recheck Comparison Review Signal Policy V1 Plan

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Goal

Selected Portfolio Dashboard의 Review Signals가 Recheck Comparison을 성과 threshold policy owner로 사용하게 한다.

이걸 하는 이유?

- 현재 Review Signals와 Recheck Comparison이 CAGR / MDD / benchmark spread threshold를 각각 계산하면 같은 recheck 결과가 서로 다른 운영 signal로 보일 수 있다.
- Performance Recheck 미실행, 실패, partial result, stale preflight, provider evidence gap은 `Clear`가 아니라 `Needs Input`, `Watch`, 또는 `Breached`로 남아야 한다.
- 이 작업은 signal 해석 강화이며, monitoring log 자동 저장이나 사용자 메모 / preset 저장 기능을 추가하지 않는다.

## Scope

- Review Signal Policy read model 추가
- Review Signals 성과 row를 Recheck Comparison rows에서 파생
- Recheck Operations Preflight route와 Provider Evidence route를 Review Signals에 연결
- Dashboard Review Signals 표시를 새 policy contract 기반으로 전환
- Focused service contract tests 추가

## Out Of Scope

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset / comment persistence
- provider / FRED / broker direct fetch
- account holdings 자동 연결
- broker order, live approval, auto rebalance
- threshold UI 설정 저장

## Completion Criteria

- Review Signals에서 CAGR / MDD / benchmark spread 자체 threshold 계산이 제거된다.
- Recheck Comparison `NOT_RUN` / error / partial evidence가 `Clear`로 보이지 않는다.
- Recheck Preflight `NEEDS_DATA` / `BLOCKED`와 Provider Evidence `REVIEW` / `NEEDS_DATA` / `BLOCKED`가 signal board에 반영된다.
- read-only execution boundary가 유지된다.
- focused service contract와 full service contract suite가 통과한다.
