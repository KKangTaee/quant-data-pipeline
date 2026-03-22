# Phase 3 First DB-Backed Runtime Validation

## 목적
이 문서는 Phase 3에서
첫 DB-backed strategy runtime 경로를 실제로 검증한 결과를 기록한다.

관련 문서:
- `.note/finance/phase3/PHASE3_MINIMAL_VALIDATION_PATH.md`
- `.note/finance/phase3/PHASE3_FIRST_DB_BACKED_STRATEGY_CANDIDATE.md`

---

## 검증 경로

실행 경로:

1. `load_price_strategy_dfs(...)`
2. `EqualWeightStrategy`
3. 결과 DataFrame 확인

---

## 검증 입력

- `symbols = ["AAPL", "MSFT", "GOOG"]`
- `start = "2024-01-01"`
- `end = "2024-12-31"`
- `timeframe = "1d"`
- `start_balance = 10000`
- `rebalance_interval = 21`

---

## 검증 결과

확인된 내용:

1. loader가 DB에서 가격 데이터를 정상 조회했다
2. adapter가 ticker-keyed strategy input dict를 정상 생성했다
3. `EqualWeightStrategy`가 예외 없이 실행됐다
4. 결과 DataFrame이 정상 생성됐다

구체 결과:
- tickers:
  - `AAPL`
  - `MSFT`
  - `GOOG`
- per-symbol row count:
  - `252`
- result row count:
  - `252`
- result columns:
  - `Date`
  - `Ticker`
  - `Close`
  - `Next Balance`
  - `End Balance`
  - `Return`
  - `Total Balance`
  - `Total Return`
  - `Rebalancing`
- final `Total Balance`:
  - `12998.14`

---

## 결론

Phase 3에서 의도한 첫 DB-backed runtime 경로,

`DB price loader -> runtime adapter -> EqualWeightStrategy`

는 현재 로컬 환경에서 정상 동작이 확인되었다.
