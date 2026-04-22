# Phase 27 Backtest Data Trust Summary First Work Unit

## 이 문서는 무엇인가

이 문서는 Phase 27의 첫 번째 작업 단위 기록이다.

목표는 Global Relative Strength와 최신 백테스트 결과 화면에서
데이터 신뢰성 정보를 더 먼저, 더 쉽게 보이게 만드는 것이다.

## 쉽게 말하면

백테스트 결과 숫자만 먼저 보여주면 사용자는 "왜 이 날짜까지만 계산됐지?"를 놓칠 수 있다.

이번 작업은 결과 상단에
요청 종료일, 실제 결과 종료일, 가격 최신성, 제외 ticker, 결측 가격 행을 먼저 보여주는 안전장치를 붙인다.

## 왜 먼저 하는가

- Phase 24 QA에서 Global Relative Strength 실행 중 ETF 가격 데이터 이슈가 실제로 나왔다.
- 일부 ticker의 최신 가격이 뒤처지면 전체 결과 기간이 짧아질 수 있다.
- missing / stale / malformed price row가 결과 해석에 영향을 주지만, 기존 화면에서는 사용자가 바로 알아보기 어려웠다.

## 이번 작업에서 바꾸는 것

### 1. runtime result window metadata

- 모든 result bundle meta에 아래 값을 남긴다.
  - `result_rows`
  - `actual_result_start`
  - `actual_result_end`

### 2. Global Relative Strength price freshness

- GRS single strategy 실행 전에 Price Freshness Preflight를 보여준다.
- GRS runtime 결과 meta에도 price freshness 결과를 저장한다.
- 가격 최신성 warning이 있으면 결과 상단 주의사항과 Data Trust Summary에서 다시 확인할 수 있게 한다.

### 3. Latest Backtest Run Data Trust Summary

- 최신 실행 결과 상단에 `Data Trust Summary`를 추가한다.
- 사용자가 결과 숫자를 보기 전에 아래를 먼저 확인할 수 있게 한다.
  - 요청 종료일
  - 실제 결과 종료일
  - 결과 row 수
  - excluded ticker 수
  - effective trading end
  - common latest price
  - newest latest price
  - latest-date spread

### 4. Data Quality Details

- excluded ticker와 malformed price row가 있으면 접을 수 있는 상세 영역에서 확인할 수 있게 한다.

## 이번 작업에서 하지 않는 것

- 결측 가격을 임의로 채우지 않는다.
- stale ticker를 자동으로 삭제하거나 universe를 자동 변경하지 않는다.
- 투자 후보 판정이나 live readiness 판단을 하지 않는다.
- compare / history / saved replay 전체 확장은 다음 작업에서 검토한다.

## 확인할 것

- `Global Relative Strength` 화면에서 Price Freshness Preflight가 보이는지
- 실행 후 `Latest Backtest Run > Data Trust Summary`가 보이는지
- 가격 최신성 warning이 있으면 사용자가 의미를 이해할 수 있는지
- `Meta`에 `price_freshness`, `actual_result_start`, `actual_result_end`, `result_rows`가 남는지

## 한 줄 정리

첫 작업은 백테스트 결과를 더 좋게 만드는 것이 아니라,
그 결과가 어떤 데이터 조건에서 나온 것인지 먼저 보이게 만드는 작업이다.
