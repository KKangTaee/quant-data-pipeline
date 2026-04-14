# Phase 17 Current Chapter TODO

## 목표

- `Value`와 `Quality + Value` strict annual family에서
  same gate lower-MDD practical candidate를 만들기 위한
  **구조 레버**를 current code 기준으로 좁힌다.
- candidate consolidation은 보조 트랙으로 검토하되,
  메인 목표는 여전히
  **낮은 `MDD`, 높은 수익률, 실전형 candidate**
  이다.

## 상태

- `completed`

## Workstream A. Structural Lever Inventory

- [x] current code 기준 구조 레버 inventory first pass
- [x] overlay / guardrail / weighting / benchmark contract 구분
- [x] strict annual current architecture에서 무엇이 already-implemented인지 정리
- [x] first implementation slice 하나로 축소

## Workstream B. Candidate Consolidation Fit Review

- [x] weighted portfolio / saved portfolio 흐름이 이미 어디까지 열려 있는지 정리
- [x] 이것이 immediate practical-candidate work에 메인 트랙인지 보조 트랙인지 판단
- [x] operator workflow bridge를 다음 phase 보조 트랙으로 넘기기로 정리

## Workstream C. Phase 17 First Implementation Slice

후보:

- [x] strict annual partial cash retention contract
- [x] strict annual defensive sleeve risk-off contract
- [x] strict annual concentration-aware weighting contract

구현 이후 다음 active step:

- [x] `Value` strongest / lower-MDD near-miss에 partial cash retention representative rerun 적용
- [x] `Quality + Value` strongest practical point에 partial cash retention representative rerun 적용
- [x] same-gate lower-MDD rescue 여부를 기준으로 next structural lever 우선순위 재판단
- [x] `Value` / `Quality + Value` anchor에 defensive sleeve representative rerun 적용
- [x] `Value` / `Quality + Value` anchor에 concentration-aware weighting representative rerun 적용
- [x] current 3개 structural lever 결과를 묶어 closeout / next-step 우선순위 정리

## 현재 판단

- 메인 트랙:
  - strict annual structural downside improvement
- 보조 트랙:
  - candidate consolidation / weighted portfolio operator bridge

## 이번 턴 기준 결론

- bounded tweak phase는 이미 끝났다
- current code를 기준으로 보면,
  `partial cash retention`, `defensive sleeve risk-off`
  와 `concentration-aware weighting`
  first three slices는 구현 완료 상태다
- representative rerun 결과:
  - `partial cash retention`은
    `MDD`를 크게 낮췄지만 return drag가 너무 컸다
  - `defensive sleeve risk-off`는
    gate는 유지했지만 `MDD`를 더 낮추지 못했다
  - `concentration-aware weighting`은
    gate는 유지했지만 current anchor에서 `MDD`를 더 낮추지 못했다
- 공통 패턴:
  - same-gate lower-MDD exact rescue는 아직 없다
  - `Value`와 `Quality + Value` current anchor는 그대로 유지된다
- closeout 판단:
  - first three slices는 practical 기준으로 충분히 확인됐다
  - 따라서 Phase 17은 closeout하고,
    다음 phase에서는
    `larger structural redesign`
    또는
    `candidate consolidation / operator bridge`
    방향을 다시 확인하는 편이 자연스럽다
- weighted portfolio / saved portfolio는 지금도 유용하지만,
  real-money gate surface가 직접 붙지 않아 immediate replacement는 아니다
