# Phase 9 Board Open Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8이 lifecycle evidence hardening을 완료했으므로, 1차 hardening cycle의 다음 약점인 cost / slippage / liquidity realism을 별도 phase로 열어야 한다.
작업을 바로 코드로 시작하기 전에, 저장 경계와 task 순서를 명확히 고정한다.

## Scope

포함한다.

- Phase 9 active board 생성
- Phase 9 task board와 immediate next task 정의
- Roadmap / root handoff log sync
- 기존 Backtest Realism 경계 확인

포함하지 않는다.

- runtime cost logic 변경
- 새 DB schema
- 새 JSONL registry
- user memo / preset persistence
- broker order / auto rebalance

## Done Criteria

- Phase 9 active phase docs가 생성된다.
- `cost-model-source-contract-review-v1`이 다음 task로 명확히 남는다.
- Roadmap이 Phase 9 active 상태를 가리킨다.
- `git diff --check`가 통과한다.
