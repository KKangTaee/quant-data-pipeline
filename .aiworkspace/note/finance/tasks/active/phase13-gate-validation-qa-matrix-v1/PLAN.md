# Phase 13 Gate Validation QA Matrix V1 Plan

Status: Complete
Created: 2026-05-30
Completed: 2026-05-30

## 이걸 하는 이유?

Phase 8~12에서 Data Coverage, Backtest Realism, Validation Efficacy, Construction Risk, Selected Monitoring evidence가 늘어났다.
하지만 evidence surface가 많아지면 `NOT_RUN`, stale, partial, missing, `NEEDS_INPUT`, `BLOCKED`, `REVIEW` 상태가 화면이나 route 사이에서 약하게 보일 위험이 있다.

이 task는 Phase 13 inventory를 기준으로 Practical Validation, Final Review, Selected Portfolio Dashboard의 gate / route / severity가 서로 맞는지 확인한다.

## Scope

포함한다.

- Practical Validation evidence surface QA
- Final Review investability packet / gate policy / selected-route QA
- Selected Portfolio Dashboard operations evidence QA
- service contract coverage 확인
- code defect 여부 판단과 후속 task handoff

포함하지 않는다.

- 코드 구현
- 새 JSONL registry
- user memo / preset persistence
- monitoring log 자동 저장
- broker order, live approval, account sync, auto rebalance
- UI redesign
- 새 데이터 provider 도입

## Done Criteria

- gate / route / severity QA matrix가 작성된다.
- 각 evidence surface가 어떤 함수와 service contract로 고정되는지 정리된다.
- non-PASS 상태가 pass처럼 처리되는 확인 결과가 남는다.
- 코드 결함이 발견되면 별도 implementation task로 넘긴다.
- Phase 13 board와 handoff docs가 다음 task `phase13-storage-data-boundary-audit-v1`를 가리킨다.
- service contract tests, diff, hygiene check가 통과한다.
