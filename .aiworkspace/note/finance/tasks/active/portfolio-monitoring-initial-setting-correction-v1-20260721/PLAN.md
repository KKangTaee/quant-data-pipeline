# Portfolio Monitoring Initial Setting Correction V1 Plan

Status: Design review

## 이걸 하는 이유?

최초 수량만 정정 가능한 현재 흐름을 시작일·시작 종가·최초 투자금까지 일관되게 바로잡는 초기 계약 정정 흐름으로 확장한다.

## 목표

- append-only 정정 이력을 유지하며 최초 시작일과 수량을 함께 수정한다.
- 새 적용 시장일과 종가를 DB-only로 결정한다.
- 이후 거래와 개별/그룹 성과를 전체 재검증·재계산한다.

## 잠정 단계

1. 초기 계약·schema·projection TDD
2. valuation/read-model/Streamlit bridge TDD
3. React correction editor와 recovery TDD
4. full regression, actual Browser QA, durable docs closeout

## 중단 조건

- written `DESIGN.md` 사용자 검토 전에는 상세 구현 계획과 production code를 작성하지 않는다.
- DB 가격 없이 날짜를 추정하거나 기존 item/registry/saved row를 덮어써야 하는 설계는 채택하지 않는다.
