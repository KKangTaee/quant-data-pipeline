# Phase 3 Statement Loader Validation

## 목적
이 문서는 Phase 3에서 구현한
financial statement broad / strict loader의 기본 검증 결과를 기록한다.

---

## 검증 함수

- `load_statement_values(...)`
- `load_statement_labels(...)`
- `load_statement_snapshot_strict(...)`

---

## 검증 입력

- `symbols = ["AAPL", "MSFT"]`
- `freq = "annual"`
- `as_of_date = "2026-03-22"`

---

## 검증 결과

### broad values
- `load_statement_values(symbols=['AAPL','MSFT'], freq='annual')`
- 결과 row 수: `203`

### broad labels
- `load_statement_labels(symbols=['AAPL','MSFT'])`
- 결과 row 수: `203`

### strict snapshot
- `load_statement_snapshot_strict(symbols=['AAPL','MSFT'], as_of_date='2026-03-22', freq='annual')`
- 결과 row 수: `138`
- 반환 symbol:
  - `AAPL`
  - `MSFT`

---

## 해석

- broad loader는 현재 상세 재무제표 raw ledger를 연구용으로 읽는 경로로 동작한다
- strict snapshot loader는 `available_at <= as_of_date` 기준으로 latest available row를 반환한다
- broad / strict 분리 정책이 실제 코드에서도 동작하는 것이 확인되었다

---

## 결론

Phase 3의 detailed financial statement loader는
현재 기준으로 broad research path와 strict PIT snapshot path 모두 기본 동작이 확인되었다.
