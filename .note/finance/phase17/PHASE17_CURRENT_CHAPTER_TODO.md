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

- `in_progress`

## Workstream A. Structural Lever Inventory

- [x] current code 기준 구조 레버 inventory first pass
- [x] overlay / guardrail / weighting / benchmark contract 구분
- [x] strict annual current architecture에서 무엇이 already-implemented인지 정리
- [x] first implementation slice 하나로 축소

## Workstream B. Candidate Consolidation Fit Review

- [x] weighted portfolio / saved portfolio 흐름이 이미 어디까지 열려 있는지 정리
- [x] 이것이 immediate practical-candidate work에 메인 트랙인지 보조 트랙인지 판단
- [ ] operator workflow bridge를 다음 phase에서 병행할지 결정

## Workstream C. Phase 17 First Implementation Slice

후보:

- [x] strict annual partial cash retention contract
- [ ] strict annual defensive sleeve risk-off contract
- [ ] strict annual concentration-aware weighting contract

구현 이후 다음 active step:

- [x] `Value` strongest / lower-MDD near-miss에 partial cash retention representative rerun 적용
- [x] `Quality + Value` strongest practical point에 partial cash retention representative rerun 적용
- [x] same-gate lower-MDD rescue 여부를 기준으로 next structural lever 우선순위 재판단
- [ ] next structural lever로 `defensive sleeve risk-off` contract 설계/구현 시작

## 현재 판단

- 메인 트랙:
  - strict annual structural downside improvement
- 보조 트랙:
  - candidate consolidation / weighted portfolio operator bridge

## 이번 턴 기준 결론

- bounded tweak phase는 이미 끝났다
- current code를 기준으로 보면,
  `partial cash retention` first slice는 구현 완료 상태다
- representative rerun 결과,
  `partial cash retention`은 `Value / Quality + Value` 모두에서
  `MDD`를 크게 낮췄지만
  current practical gate를 rescue하진 못했다
- 공통 패턴:
  - downside protection은 분명했다
  - 하지만 현금 비중이 많이 남으면서 `CAGR` drag가 커졌다
  - `benchmark_policy` / `liquidity_policy` caution도 함께 남았다
- 따라서 다음 active question은
  idle cash drag를 줄이면서 downside를 보완할 수 있는
  `defensive sleeve risk-off` contract를 여는 것이다
- weighted portfolio / saved portfolio는 지금도 유용하지만,
  real-money gate surface가 직접 붙지 않아 immediate replacement는 아니다
