# Phase 3 Fundamentals / Factors Review And Direction

## 목적
이 문서는 `nyse_fundamentals`, `nyse_factors`의 현재 상태를 재점검하고,
앞으로의 올바른 역할과 방향을 고정하기 위한 기준 문서다.

---

## 결론 요약

현재 판단은 다음과 같다.

- `nyse_fundamentals`는 유지한다
- `nyse_factors`도 유지한다
- 다만 둘 다 **raw ledger가 아니라 broad research layer**로 정의해야 한다
- strict point-in-time 원장은 여전히
  - `nyse_financial_statement_filings`
  - `nyse_financial_statement_values`
  - `nyse_financial_statement_labels`
  가 담당한다

즉 역할 분리는 아래가 맞다.

```text
raw ledger:
  nyse_financial_statement_filings
  nyse_financial_statement_values
  nyse_financial_statement_labels

summary layer:
  nyse_fundamentals

derived factor layer:
  nyse_factors
```

---

## 왜 없애지 않았는가

`nyse_fundamentals`, `nyse_factors`를 없애고
상세 재무제표 raw ledger로 전부 대체하는 방향도 검토했다.

하지만 현재는 그렇게 하지 않았다.

이유:
- 현재 상세 재무제표 raw ledger coverage가 아직 매우 낮다
  - 현재 DB 기준 `nyse_financial_statement_values`는 2개 symbol 수준
- 반면 `nyse_fundamentals`, `nyse_factors`는 broad universe coverage를 이미 제공한다
- 따라서 지금 단계에서는
  - raw ledger를 strict / deep source of truth로 두고
  - fundamentals / factors는 broad research layer로 유지하는 것이 현실적이다

즉 지금 당장 필요한 것은 제거가 아니라 **역할 재정의와 품질 보강**이다.

---

## 기존 상태의 문제

## 1. 역할 의미가 애매했다

기존 테이블은 사실상 아래 성격이었지만, 코드와 문서에서 충분히 분리되어 있지 않았다.

- `nyse_fundamentals`
  - yfinance 기반 period-end summary snapshot
- `nyse_factors`
  - `nyse_fundamentals + asof price` 기반 파생 팩터

하지만 strict PIT safe table처럼 오해될 여지가 있었다.

---

## 2. summary row 품질이 약했다

기존 `upsert_fundamentals(...)`는
모든 핵심 값이 비어 있는 blank row도 들어갈 수 있었다.

실제 예:
- `AAPL annual 2021-09-30` blank row가 남아 있었다

이런 row는 downstream factor 계산에서 무의미한 null row를 만들고,
row count를 왜곡한다.

---

## 3. factor set이 얇았다

기존 factor table은 기본 valuation / quality 일부만 담고 있었다.

부족했던 점:
- yield형 팩터 부족
- margin 계열 부족
- growth 계열 부족
- price attachment metadata 부족

즉 price-only 전략 이후 factor 전략으로 넘어가기에 아직 얇은 상태였다.

---

## 4. source / derivation 메타가 부족했다

예:
- `gross_profit`이 direct인지 derived인지
- `free_cash_flow`가 direct인지 OCF-CAPEX derived인지
- `shares_outstanding`이 issued-minus-treasury인지 average shares fallback인지

같은 정보가 저장되지 않았다.

이건 미래에 factor 결과를 해석하거나 품질을 비교할 때 불리하다.

---

## 이번에 적용한 수정

## A. `nyse_fundamentals` hardening

추가/보강한 내용:
- blank summary row 적재 방지
- 기존 symbol/freq 기록을 canonical refresh 방식으로 재적재 가능하게 수정
- base field 확장:
  - `pretax_income`
  - `interest_expense`
  - `inventory`
  - `short_term_debt`
  - `long_term_debt`
  - `shareholders_equity`
- derivation/source 메타 추가:
  - `source_mode`
  - `timing_basis`
  - `gross_profit_source`
  - `operating_income_source`
  - `ebit_source`
  - `free_cash_flow_source`
  - `shares_outstanding_source`
  - `total_debt_source`
  - `shareholders_equity_source`

현재 테이블 의미:
- broad coverage summary layer
- `period_end` 기반 provider-normalized summary
- strict PIT safe table은 아님

---

## B. `nyse_factors` hardening

추가/보강한 내용:
- 기존 symbol/freq 기록을 canonical refresh 방식으로 재계산 가능하게 수정
- price attachment metadata 추가:
  - `price_date`
  - `price_match_gap_days`
  - `price_source`
  - `price_timeframe`
  - `timing_basis`
  - `pit_mode`
- factor set 확장:
  - valuation / yield:
    - `sales_yield`
    - `earnings_yield`
    - `operating_income_yield`
    - `book_to_market`
    - `ocf_yield`
    - `fcf_yield`
  - safety / leverage:
    - `cash_ratio`
    - `debt_to_assets`
    - `net_debt`
    - `net_debt_to_equity`
  - margin / profitability:
    - `gross_margin`
    - `operating_margin`
    - `net_margin`
    - `ocf_margin`
    - `fcf_margin`
  - growth:
    - `revenue_growth`
    - `gross_profit_growth`
    - `net_income_growth`
    - `fcf_growth`
  - `interest_coverage`도 이제 raw `interest_expense`가 있으면 계산

현재 테이블 의미:
- broad research derived factor layer
- `period_end` 기준 summary 재무 + as-of price 결합 결과
- strict PIT factor store는 아님

---

## 현재 유효한 방향

## `nyse_fundamentals`

권장 역할:
- broad universe coverage용 normalized summary
- factor calculation의 base table
- UI / loader / research에서 빠르게 쓰는 중간 계층

권장하지 않는 역할:
- raw truth
- filing-accurate strict PIT source

---

## `nyse_factors`

권장 역할:
- broad research용 파생 팩터 저장소
- loader 기반 factor ranking / screening 실험 입력
- 초기 factor 전략 prototype 입력

권장하지 않는 역할:
- filing-safe production-grade PIT factor source

---

## `nyse_financial_statement_*`

권장 역할:
- strict raw ledger
- point-in-time 강화의 원장
- 장기적으로 `nyse_fundamentals` 재구성의 source of truth 후보

즉 이 세트는 fundamentals/factors를 대체하는 것이 아니라,
장기적으로 **더 정확한 normalized summary / factor builder의 upstream source**가 된다.

---

## 검증 결과

샘플 검증 대상:
- `AAPL`
- `MSFT`

검증한 것:
- annual fundamentals 재적재
- annual factors 재계산
- quarterly fundamentals / factors 샘플 적재

확인된 결과:
- 새 컬럼들이 실제 DB에 생성됨
- `source_mode`, `timing_basis`, `*_source` 메타가 저장됨
- `price_date`, `price_match_gap_days`, `pit_mode`가 factor row에 저장됨
- blank annual row였던 `AAPL 2021-09-30`는 canonical refresh 후 제거됨
- annual sample 기준 fundamentals / factors row count가 다시 1:1로 맞춰짐

샘플 annual 결과:
- `AAPL annual`: 4 rows (`2022-09-30 ~ 2025-09-30`)
- `MSFT annual`: 4 rows (`2022-06-30 ~ 2025-06-30`)

---

## 아직 남아 있는 것

## 1. full-universe backfill

이번에는 코드와 샘플 검증을 우선했다.

즉:
- 새 스키마 / 새 계산식 / 새 refresh 규칙은 들어갔지만
- 기존 전체 universe row를 아직 전부 재수집 / 재계산한 것은 아니다

따라서 전체 테이블을 완전히 canonical 상태로 만들려면
후속 운영 작업으로:

1. `upsert_fundamentals(..., replace_symbol_history=True)`
2. `upsert_factors(..., replace_symbol_history=True)`

를 full universe 기준으로 다시 돌리는 backfill이 필요하다.

---

## 2. strict PIT factor path

현재 `nyse_factors`는 여전히 broad research mode다.

장기적으로 strict PIT factor 전략을 하려면:
- `nyse_financial_statement_values`
- `nyse_financial_statement_filings`
- `available_at`

를 기준으로 snapshot을 만들고
별도의 strict factor build path가 필요하다.

즉 현재 보강은 “연구용 broad layer 강화”이지
strict PIT final state는 아니다.

---

## 권장 운영 원칙

당분간은 아래처럼 쓰는 것이 좋다.

- broad factor research / ranking / prototype 전략:
  - `nyse_fundamentals`
  - `nyse_factors`

- strict point-in-time 검증 / 장기 고도화:
  - `nyse_financial_statement_filings`
  - `nyse_financial_statement_values`
  - `nyse_financial_statement_labels`

즉 현재 broad layer와 strict raw ledger를 분리해서 쓰는 것이 맞다.

---

## 최종 결론

현재 단계에서 가장 합리적인 방향은:

1. `nyse_fundamentals` 유지
2. `nyse_factors` 유지
3. 둘을 raw ledger가 아닌 broad research layer로 명확히 정의
4. detailed statement raw ledger는 strict source of truth로 유지
5. 장기적으로 statement-led normalized summary / strict factor pipeline으로 확장

즉 이번 작업의 핵심 성과는
이 두 테이블을 없앤 것이 아니라,
**의미를 바로잡고, 컬럼/계산/메타를 보강해서 앞으로 factor 전략에 쓸 수 있는 형태로 재정비한 것**이다.
