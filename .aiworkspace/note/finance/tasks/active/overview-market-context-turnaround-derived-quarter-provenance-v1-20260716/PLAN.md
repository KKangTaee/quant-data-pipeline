# Overview Market Context Turnaround Derived Quarter Provenance V1

Status: Design Review
Last Updated: 2026-07-16

## Goal

SEC 공시의 동등한 concept 계열에서 FY와 Q1~Q3가 서로 다른 taxonomy 이름을 사용해도, 엄격한 회계·기간 조건을 만족하면 Q4를 공시 기반으로 산출한다. 산출된 분기와 이를 포함한 TTM 지표는 화면에서 직접 공시값과 구분한다.

## 이걸 하는 이유?

Moderna 2023년 매출은 Q1/Q2의 `Revenues`와 Q3/FY의 `RevenueFromContractWithCustomerExcludingAssessedTax`로 concept 이름이 바뀐다. 현재 resolver는 exact concept별로만 FY 차감을 수행하여 실제 공시 숫자가 모두 있어도 2023-Q4 매출을 만들지 못하고, 그 한 분기 때문에 네 개 TTM 구간이 끊긴다. 그래프의 결측 보존 원칙은 유지하면서, 동일 의미로 명시된 concept family 안의 확정 공시값을 안전하게 사용할 필요가 있다.

## Scope

- `resolve_discrete_quarters`의 동등 concept-family Q4 fallback
- derived-quarter 및 TTM 포함 여부의 구조화 provenance
- 전환분석 차트와 inspector의 `공시 기반 산출` 표기
- MRNA 회귀 테스트, 기존 exact-concept/결측/PIT 회귀 테스트
- 실제 DB와 desktop/420px Browser QA

## Out Of Scope

- 결측값 보간 또는 forecast
- 임의 taxonomy concept 자동 유사도 매칭
- schema, collector, provider, DB row 변경
- 직접 공시값을 산출값으로 대체
- universe-wide backfill 또는 진단 job panel

## Tentative Roadmap

1. MRNA 회귀 fixture와 안전 조건을 RED 테스트로 고정한다.
2. 동등 concept-family Q4 산출과 provenance를 구현한다.
3. 차트/inspector에 중립적인 산출 표기를 추가한다.
4. focused regression, actual DB, Browser QA와 문서 정렬을 수행한다.

## Stop Condition

- 직접 Q4가 없고 FY/Q1/Q2/Q3가 모두 primary filing facts이며 symbol, fiscal year, unit, concept family가 맞을 때만 Q4가 산출된다.
- 산출값의 `available_at`은 모든 operand가 이용 가능해진 날짜보다 빠르지 않다.
- MRNA 2023-Q4 매출 `2.811B`, 원가 `0.929B`, GP `1.882B`, 영업이익 `0.006B`가 재현된다.
- 산출 분기와 해당 분기를 포함한 TTM 표시가 직접 공시와 구분된다.
- 안전 조건이 맞지 않으면 기존 결측과 끊긴 선을 유지한다.
