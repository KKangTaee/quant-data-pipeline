# Phase 27 Completion Summary

## 목적

이 문서는 Phase 27 `Data Integrity And Backtest Trust Layer`를 closeout 시점에 정리하기 위한 문서다.

Phase 27은 사용자 QA까지 완료된 상태다.

## 진행 상태

- `complete`

## 검증 상태

- `manual_qa_completed`

## 이번 phase에서 완료한 것

### 1. Backtest Data Trust Summary 첫 구현

- result bundle meta에 실제 결과 기간과 row 수를 남긴다.
- 최신 실행 결과 상단에 데이터 신뢰성 요약을 보여주는 UI를 추가했다.
- `Requested End`, `Actual Result End`, `Result Rows`, `Excluded Tickers`를 결과 해석 전에 확인할 수 있게 했다.

쉽게 말하면:

- 사용자가 수익률 숫자를 보기 전에, 이번 결과가 어느 데이터 기간으로 계산됐는지 먼저 확인할 수 있게 한다.

### 2. Global Relative Strength price freshness 연결

- GRS single strategy 화면에 price freshness preflight를 연결했다.
- GRS runtime 결과에도 price freshness metadata를 남긴다.
- stale / missing ticker가 있을 때 실행 전후에 같은 데이터 조건을 확인할 수 있게 했다.

쉽게 말하면:

- ETF universe 중 어떤 ticker의 가격 데이터가 뒤처져 있는지 실행 전후에 더 쉽게 볼 수 있다.

### 3. Data Quality Details 확인

- excluded ticker가 있으면 어떤 ticker가 제외됐는지 `Data Quality Details`에서 확인할 수 있게 했다.
- malformed / missing price row가 있으면 ticker와 날짜 정보를 확인할 수 있게 했다.

쉽게 말하면:

- 결과가 이상해 보일 때, 먼저 데이터가 빠졌는지 / 제외됐는지 확인할 수 있다.

## Phase 28로 넘기는 것

- warning 문구 추가 한글화 / 설명 정리 확대
- compare / history / saved replay에서 Data Trust Summary를 어느 수준까지 유지할지 검토
- strict annual / quarterly / 신규 ETF 전략 preflight 표현 정리

## closeout 판단

Phase 27은 closeout한다.

사용자가 Phase 27 checklist QA를 완료했다.
다음 phase는 `Phase 28 Strategy Family Parity And Cadence Completion`으로 여는 것이 자연스럽다.
