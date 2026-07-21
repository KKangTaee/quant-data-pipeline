# Market Movers Non-Daily Refresh Basis Fix V1 Plan

Status: In Progress
Last Updated: 2026-07-21

## 이걸 하는 이유?

주간·월간 변동 종목은 일부 최신 가격만 저장된 날을 랭킹 기준일로 사용할 수 없어 `effective_end_date`가 2026-07-07로 후퇴한다. 현재 화면은 이 랭킹 기준일을 가격 수집 목표일에도 재사용해, 실제로는 최신 가격 보강이 필요해도 `가격 이력 수동 갱신`이 사라지는 순환 문제가 있다.

## Goal

- 가격 수집 목표일은 최신 완료 NYSE 거래일을 사용한다.
- 랭킹 데이터 기준일은 universe coverage를 충족한 `effective_end_date`를 유지한다.
- 비-Daily 화면에서 가격 이력 수동 갱신 액션을 항상 찾을 수 있게 한다.
- 시장 기준일과 데이터 기준일을 서로 다른 의미로 표시한다.

## Non-Goals

- coverage 임계치 변경
- provider 또는 DB schema 변경
- 불완전한 최신일을 랭킹에 강제 포함
- 자동 스케줄러 추가

## Implementation Tasks

1. 최신 완료 NYSE 거래일과 랭킹 기준일 분리 계약을 회귀 테스트로 고정한다.
2. Overview action/helper의 preflight·action·timing 계산을 수정한다.
3. focused pytest, compile, diff check, React/Browser QA를 수행한다.
4. runbook과 handoff 문서를 동기화하고 coherent commit을 만든다.

## Stop Condition

- 비-Daily preflight가 snapshot effective date가 아니라 최신 완료 NYSE session을 사용한다.
- `market_date`와 `data_as_of`가 각각 시장 완료일과 랭킹 기준일을 표현한다.
- selected symbol 수가 0이어도 가격 이력 수동 갱신 액션은 유지된다.
- focused tests와 정적 검증이 통과한다.
