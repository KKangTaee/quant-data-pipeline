# Phase 26 Next Phase Preparation

## 목적

이 문서는 Phase 26 이후 어떤 질문으로 Phase 27을 여는 것이 자연스러운지 정리하기 위한 handoff 문서다.

현재 예상되는 Phase 27은 `Data Integrity And Backtest Trust Layer`다.

## 현재 handoff 상태

- Phase 25까지 Pre-Live Review workflow는 닫혔다.
- Phase 26에서는 과거 backlog와 현재 foundation gap을 다시 정리했다.
- Phase 26 결과, 가장 먼저 다룰 영역은 데이터 신뢰성과 백테스트 preflight로 정리되었다.
- Phase 27 구현은 Phase 26 checklist QA 이후 시작한다.

## 다음 phase에서 더 중요한 질문

1. 백테스트를 실행하기 전에 데이터가 어느 날짜까지 신뢰 가능한지 보여줄 수 있는가
2. missing ticker, stale price, malformed row, common-date truncation을 사용자가 놓치지 않게 할 수 있는가
3. 결과가 좋거나 나쁠 때 전략 문제와 데이터 문제를 분리해서 볼 수 있는가

## 추천 다음 방향

Phase 27은 `Data Integrity And Backtest Trust Layer`가 자연스럽다.

이유:

- Phase 24 QA에서 `EEM`, `IWM`, common-date truncation 문제가 실제로 드러났다.
- 전략과 후보 검토를 더 늘리기 전에 데이터 경고와 백테스트 가능 범위를 더 명확히 해야 한다.
- 후보 추천 프로그램으로 가려면 "결과가 믿을 만한가"를 먼저 답할 수 있어야 한다.

## handoff 메모

- Phase 27은 투자 분석 phase가 아니라 데이터 / 백테스트 신뢰성 강화 phase다.
- Live Readiness / Final Approval은 Phase 30 이후로 둔다.
