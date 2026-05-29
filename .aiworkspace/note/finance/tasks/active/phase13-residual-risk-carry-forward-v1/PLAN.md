# Phase 13 Residual Risk / Carry-Forward V1 Plan

Status: Complete
Created: 2026-05-30
Completed: 2026-05-30

## 이걸 하는 이유?

Phase 8~12의 1차 hardening cycle은 단순 백테스트 탐색을 investability evidence workflow로 강화했다.
하지만 개선된 부분과 아직 구현되지 않은 broker-grade / production-grade 기능을 섞어서 말하면, 최종 closeout이 실제보다 과장될 수 있다.

이 task의 목적은 새 기능을 만들지 않고, 1차 cycle 이후에도 남는 한계를 명확히 분류하는 것이다.
13-6 final closeout은 이 matrix를 기준으로 "완료된 개선"과 "다음 cycle로 넘길 작업"을 구분한다.

## Scope

포함한다.

- Phase 8~12 residual risk 수집
- Phase 13 13-1 inventory, 13-2 QA matrix, 13-3 storage audit, 13-4 docs alignment 결과 통합
- current product limitation / second-cycle candidate / explicit out-of-scope 분리
- 13-6 final closeout에서 사용할 safe statement 기준 정리

포함하지 않는다.

- 코드 구현
- 새 phase 생성
- 새 JSONL registry
- user memo / preset persistence
- monitoring log 자동 저장
- broker order, live approval, account sync, auto rebalance
- paid data source 도입 결정

## Done Criteria

- carry-forward matrix가 작성된다.
- Phase 13 board가 13-5 complete, 13-6 next로 갱신된다.
- roadmap / index / root handoff log가 다음 task를 가리킨다.
- hygiene / diff / service contract 검증이 통과한다.
