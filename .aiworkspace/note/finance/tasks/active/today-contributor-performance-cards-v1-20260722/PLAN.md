# Today Contributor Performance Cards V1 Plan

Status: Implementation Plan Ready
Roadmap: 1/4 complete
Last Updated: 2026-07-22

## 이걸 하는 이유?

Today의 `누적 기여`는 현재 종목명과 달러 기여금만 작은 chip으로 표시한다. 사용자는 이 값을 종목 수익률로 읽기 쉽고, 실제 종목 성과와 포트폴리오에 미친 금액 효과를 구분하기 어렵다. 대표 포트폴리오를 빠르게 판단하려면 두 단위를 한 카드에서 분명하게 분리해야 한다.

## Goal

기여 상위 2개와 하위 2개 종목을 compact performance card로 표시하고, 각 카드에서 현금흐름 조정 종목 누적 수익률과 포트폴리오 누적 기여금을 서로 다른 label과 hierarchy로 읽게 한다.

## Scope

- Portfolio Monitoring item row에 개별 lane의 현금흐름 조정 누적 수익률을 additive field로 제공
- Today contributor projection에 명시적인 `contribution_value`와 `total_return` 제공
- `누적 기여`를 `종목별 성과 기여` 카드 grid로 교체
- 상위 양수 2개, 하위 음수 2개 selection 유지
- React primary와 read-only fallback 모두 단위/label 개선
- desktop, 760px, 420px actual Browser QA

## Out Of Scope

- 활성 종목 전체 목록 노출
- 기여금 계산식, 포트폴리오 수익률, 종목 lane 계산식 변경
- Portfolio Monitoring 본 화면 개편
- provider fetch, DB schema, ingestion, 주문·리밸런싱 기능

## Roadmap

1. **계약·카드 설계 (`1/4차`, 완료)**: 수익률과 기여금의 의미, fallback, responsive contract 확정.
2. **Python 성과 계약 (`2/4차`)**: item lane return과 Today projection을 TDD로 확장.
3. **React 카드 구현 (`3/4차`)**: compact contributor cards와 empty/partial state 구현.
4. **Browser QA·문서 정렬 (`4/4차`)**: 1280/760/420, overflow, console, regression 확인.

## Stop Condition

상위·하위 contributor 카드에서 `종목 누적 수익률`과 `포트폴리오 누적 기여`가 명확히 분리되고, 현금흐름이 있는 종목도 단순 현재가/최초금액 비율이 아닌 lane의 flow-adjusted return을 사용하며, 기존 Today와 Portfolio Monitoring 계약 회귀 없이 actual Browser QA를 통과하면 종료한다.
