# Phase 4 Extended Statement Refresh Verification And Shadow Rebuild

## 목적
이 문서는 사용자가 직접 실행한

- `Extended Statement Refresh (annual, periods=12)`
- `Extended Statement Refresh (quarterly, periods=12)`

이 sample universe 기준으로 실제로 얼마나 반영되었는지 확인하고,
그 직후 shadow fundamentals/factors를 다시 빌드한 결과를 정리한다.

대상 universe:
- `AAPL`
- `MSFT`
- `GOOG`

---

## 1. Refresh 후 statement coverage 확인

### annual strict coverage

- `AAPL`
  - `min_period_end = 2021-09-25`
  - `max_period_end = 2025-09-27`
  - `distinct_period_ends = 5`
- `GOOG`
  - `min_period_end = 2021-12-31`
  - `max_period_end = 2025-12-31`
  - `distinct_period_ends = 6`
- `MSFT`
  - `min_period_end = 2023-12-31`
  - `max_period_end = 2025-06-30`
  - `distinct_period_ends = 9`

### quarterly strict coverage

- `AAPL`
  - `min_period_end = 2024-09-28`
  - `max_period_end = 2025-12-27`
  - `distinct_period_ends = 6`
- `GOOG`
  - `min_period_end = 2024-06-30`
  - `max_period_end = 2025-09-30`
  - `distinct_period_ends = 6`
- `MSFT`
  - `min_period_end = 2024-09-30`
  - `max_period_end = 2025-12-31`
  - `distinct_period_ends = 6`

---

## 2. 해석

이번 refresh는 정상적으로 반영되었다.

하지만 coverage 의미는 분명하다.

- `annual`
  - sample universe 기준으로는 usable history가 `2021~2023` 이후부터 시작
- `quarterly`
  - sample universe 기준으로는 usable history가 `2024` 이후부터 시작

즉 현재 local ledger 기준으로는:
- annual strict path가 quarterly strict path보다 더 이른 구간까지 usable
- 그렇더라도 아직 `2016` 시작 statement-driven quality backtest를 열 수준은 아니다

---

## 3. Shadow rebuild 결과

refresh 후 아래 shadow rebuild를 다시 실행했다.

- `upsert_statement_fundamentals_shadow(..., freq='annual')`
- `upsert_statement_factors_shadow(..., freq='annual')`
- `upsert_statement_fundamentals_shadow(..., freq='quarterly')`
- `upsert_statement_factors_shadow(..., freq='quarterly')`

결과:

### annual shadow
- fundamentals rows written: `12`
- factors rows written: `12`
- shadow factor rows 중 `market_cap` non-null: `10`

### quarterly shadow
- fundamentals rows written: `18`
- factors rows written: `18`
- shadow factor rows 중 `market_cap` non-null: `14`

의미:
- refresh로 확보한 statement history는 shadow path에 정상 반영됨
- quarterly path도 이제 shadow fundamentals/factors 기준으로는 usable

---

## 4. Strategy prototype 재검증

### annual statement-driven quality prototype

조건:
- `start = 2023-01-01`
- `end = 2026-03-20`
- `statement_freq = annual`

결과:
- `first_active = 2023-01-31`
- `End Balance = 23645.4`
- `CAGR = 0.316218`
- `Sharpe Ratio = 1.587924`

### quarterly statement-driven quality prototype

조건:
- `start = 2024-01-01`
- `end = 2026-03-20`
- `statement_freq = quarterly`

결과:
- `first_active = 2024-10-31`
- `End Balance = 13952.3`
- `CAGR = 0.169015`
- `Sharpe Ratio = 0.874793`

---

## 5. 결론

현재 sample-universe 기준으로는:

- `annual` strict statement quality path가
  실질적으로 더 usable하다
- `quarterly` strict path도 동작은 하지만
  first active date가 더 늦다

즉 지금 다음 판단은 이렇게 보는 게 맞다.

1. 더 긴 backtest / 더 이른 active date가 필요하면
   - annual coverage를 더 늘리는 쪽이 우선
2. quarterly prototype은 이미 열렸지만
   - 현재 coverage로는 public 후보로 올리기엔 아직 이르다

현재 추천:
- 다음 확대 작업은 `statement coverage 확장` 기준으로 계속 가는 것이 맞다
