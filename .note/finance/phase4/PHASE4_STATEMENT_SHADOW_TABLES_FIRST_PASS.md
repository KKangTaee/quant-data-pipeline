# Phase 4 Statement Shadow Tables First Pass

## 목적
이 문서는 `statement-driven fundamentals/factors backfill`을
현재 public broad-research 테이블을 덮어쓰지 않고
shadow table로 여는 first-pass 구현 기록이다.

이번 단계의 목표:
- `nyse_fundamentals_statement`
- `nyse_factors_statement`

두 shadow table을 실제 code path와 validation까지 포함해 연다.

---

## 이번에 추가된 것

### 1. schema

추가된 schema:
- `finance_fundamental.nyse_fundamentals_statement`
- `finance_fundamental.nyse_factors_statement`

의미:
- broad public row를 유지한 채
- statement-driven row를 별도 저장하는 shadow layer

핵심 메타:
- `nyse_fundamentals_statement`
  - `latest_available_at`
  - `latest_accession_no`
  - `latest_form_type`
  - `source_mode='statement_ledger_shadow'`
  - `timing_basis='latest_available_for_period_end'`
- `nyse_factors_statement`
  - `fundamental_available_at`
  - `fundamental_accession_no`
  - `pit_mode='statement_derived_shadow'`

---

### 2. data-layer build / upsert

추가된 함수:
- `finance/data/fundamentals.py`
  - `_load_statement_values_strict_history_mysql(...)`
  - `build_fundamentals_history_from_statement_values(...)`
  - `upsert_statement_fundamentals_shadow(...)`
- `finance/data/factors.py`
  - `load_statement_fundamentals_shadow_mysql(...)`
  - `upsert_statement_factors_shadow(...)`

흐름:

```text
nyse_financial_statement_values
  -> strict usable rows only
  -> latest row per symbol / period_end / concept
  -> normalized fundamentals history
  -> nyse_fundamentals_statement
  -> as-of price attach
  -> derived factors
  -> nyse_factors_statement
```

---

### 3. loader read boundary

추가된 loader:
- `finance/loaders/fundamentals.py`
  - `load_statement_fundamentals_shadow(...)`
- `finance/loaders/factors.py`
  - `load_statement_factors_shadow(...)`

의미:
- shadow write path를 실제 reader로 바로 검증할 수 있게 함
- 아직 public UI 전략 입력으로는 연결하지 않음

---

## sample-universe 검증

대상:
- `AAPL`
- `MSFT`
- `GOOG`
- `freq='annual'`

실행 결과:
- `upsert_statement_fundamentals_shadow(...)`
  - `12` rows written
- `upsert_statement_factors_shadow(...)`
  - `12` rows written

loader 검증:
- `load_statement_fundamentals_shadow(...)`
  - `(12, 39)` shape
- `load_statement_factors_shadow(...)`
  - `(12, 53)` shape

확인된 의미:
- accounting quality 중심 필드
  - `gross_margin`
  - `operating_margin`
  - `roe`
  - `debt_ratio`
  는 정상적으로 채워짐
- `latest_available_at` / `fundamental_available_at` 메타도 같이 남음
- 이후 first-pass shares enhancement로
  broad `nyse_fundamentals`의 nearest-period `shares_outstanding` fallback도 연결되었다
- 따라서 sample-universe 기준 valuation 계열 `market_cap`, `per`, `pbr`도 상당 부분 채워진다

---

## 현재 한계

### shares / market_cap

현재는 broad fallback 보강으로
`shares_outstanding`과 `market_cap`이 상당 부분 채워지지만,
이 값은 strict statement direct가 아니라
`broad fundamentals nearest-period fallback`이 섞인 hybrid 의미를 가진다.

즉 현재 shadow factor table은:
- quality / accounting ratio 관점에서는 유효
- valuation factor도 일부 읽을 수 있음
- 다만 strict statement-only valuation history는 아직 아님

### timing 의미

이 경로는 strict as-of snapshot store 그 자체는 아니다.

현재 의미:
- `period_end`별로
- 해당 period에 대해 현재 ledger 안에서 가장 늦은 `available_at` row를 사용

즉 정확한 해석은:
- `strict PIT raw ledger`를 source로 쓰는 shadow rebuild
- 하지만 output table 자체는
  `latest_available_for_period_end` 성격의 summary/derived history

---

## 결론

이번 단계로 인해:
- public broad-research `nyse_fundamentals` / `nyse_factors`는 유지되고
- 별도로 statement-driven shadow path가 실제 DB write/read 수준으로 열렸다

현재 상태:
- broad public path와 strict statement prototype path를 병렬로 비교할 수 있음
- 다음 핵심은
  - coverage 확대
  - shares/valuation 보강 여부 판단
  - public 후보 승격 여부 판단
  이다
