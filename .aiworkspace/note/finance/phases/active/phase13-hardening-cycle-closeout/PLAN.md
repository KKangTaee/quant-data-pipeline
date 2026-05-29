# Phase 13 First-Cycle Hardening Closeout Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 8부터 Phase 12까지는 처음 문제의식이었던 "백테스트 중심 탐색만으로는 실전 투자 판단이 부족하다"는 약점을 줄이기 위한 1차 hardening cycle이었다.
각 phase는 lifecycle / survivorship, cost / liquidity realism, temporal validation, construction risk, selected monitoring을 각각 강화했다.

Phase 13의 목적은 새 기능을 급히 추가하는 것이 아니라, 이 1차 개선이 하나의 제품 흐름으로 닫혔는지 검증하고 다음 개발 사이클로 넘길 residual risk와 carry-forward task를 명확히 분리하는 것이다.

이 phase는 live approval, broker order, auto rebalance를 만들지 않는다.
또한 user memo, preset, monitoring log auto-write, 의미 없는 JSONL 저장을 늘리는 작업이 아니다.

## Phase Goal

Phase 13은 아래 질문에 답한다.

- Phase 8~12가 원래 약점을 어떤 수준까지 줄였는가?
- Practical Validation, Final Review, Selected Dashboard gate / route / severity가 서로 일관적인가?
- `NOT_RUN`, stale, partial, missing, blocked evidence가 pass처럼 보이지 않는가?
- DB-backed data와 workflow JSONL compact evidence의 경계가 유지되는가?
- 오래 유지될 docs / runbooks / roadmap이 현재 상태를 정확히 설명하는가?
- 1차 사이클에서 해결하지 못한 risk와 2차 사이클 후보는 무엇인가?

## Scope

포함한다.

- Phase 8~12 closeout inventory
- gate / validation QA 기준 정리
- storage / data boundary audit
- docs / runbook sync plan
- residual risk / carry-forward matrix
- integrated QA / 1차 cycle closeout

포함하지 않는다.

- 새 JSONL registry
- user memo / preset persistence
- monitoring log 자동 저장
- live approval, broker order, auto rebalance
- account / broker integration
- 신규 데이터 provider 도입
- 새로운 strategy / optimizer 구현
- UI polish나 dashboard redesign

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| 13-0 | Phase 13 board open / scope and task split | Complete |
| 13-1 | Phase 8~12 improvement inventory | Complete |
| 13-2 | Gate / validation QA matrix | Complete |
| 13-3 | Storage / data boundary audit | Complete |
| 13-4 | Docs / runbook alignment | Next |
| 13-5 | Residual risk / carry-forward triage | Pending |
| 13-6 | Phase 13 integrated QA / final closeout | Pending |

## Done Criteria

- Phase 8~12의 구현 결과가 하나의 inventory로 정리된다.
- Gate / route / severity QA에서 주요 non-PASS evidence가 pass처럼 숨지 않는지 확인된다.
- 저장 경계가 재확인된다: registry / saved setup / monitoring log / report / user memo / preset이 역할을 넘지 않는다.
- `docs/`, phase docs, task docs, runbooks, root handoff logs가 1차 cycle 완료 상태를 가리킨다.
- 남은 risk가 "현재 부족한 점"과 "2차 개선 후보"로 분리된다.
- service contract / boundary / hygiene / diff 검증이 통과한다.

## Carry Forward To Later Cycles

- broker/account integration, tax-lot handling, optimizer, broker-grade rebalance, production monitoring alerts, paid / premium data source는 Phase 13의 구현 대상이 아니다.
- 필요한 경우 Phase 13 closeout 이후 2차 개선 cycle로 별도 phase를 연다.
