# Phase 7 Statement Source Payload Inspection

## 목적

- 현재 statement source가 실제로 어떤 timing field를 주는지 다시 확인한다.
- quarterly late-start 문제가 source 부족인지, DB/loader semantics 문제인지 구분한다.

## inspected path

- source helper: `finance.data.financial_statements.inspect_financial_statement_source(...)`
- provider: EDGAR facts + filings path
- inspection symbols:
  - `AAPL`
  - `MSFT`
  - `GOOG`
  - `NVDA`
  - `JPM`

## 핵심 결과

source는 late-start의 근본 원인이 아니었다.

- `AAPL`
  - `statement_fact_count = 11,362`
  - `filing_count = 130`
- `MSFT`
  - `statement_fact_count = 13,402`
  - `filing_count = 135`
- `GOOG`
  - `statement_fact_count = 7,044`
  - `filing_count = 44`
- `NVDA`
  - `statement_fact_count = 11,431`
  - `filing_count = 110`
- `JPM`
  - `statement_fact_count = 9,402`
  - `filing_count = 135`

즉 source 자체에는 이미 긴 history가 있다.

## timing field inventory

`inspect_financial_statement_source()` 기준으로 확인한 결과:

- fact layer:
  - `period_start`
  - `period_end`
  - `filing_date`
  - `accession`
  - `unit`
  - `numeric_value`
- filing layer:
  - `filing_date`
  - `accepted_at`
  - `available_at`
  - `report_date`

예: `AAPL`

- `facts_with_period_start = 8,018`
- `facts_with_period_end = 11,362`
- `facts_with_filing_date = 11,362`
- `facts_with_accession = 11,362`
- `filings_with_accepted_at = 130`
- `filings_with_available_at = 130`
- `filings_with_report_date = 130`

따라서 현재 raw ledger가 필요로 하는 PIT timing field는 source에서 실제로 반환되고 있다.

## fiscal period observation

inspection 결과, quarterly history를 복구하려면 `FY`를 무시하면 안 된다.

예: `AAPL`

- `FY = 3,736`
- `Q3 = 2,756`
- `Q2 = 2,577`
- `Q1 = 2,068`

예: `MSFT`

- `FY = 3,861`
- `Q2 = 3,571`
- `Q3 = 3,377`
- `Q1 = 2,155`

해석:

- EDGAR facts에서는 year-end quarter가 `10-K` + `FY` 형태로 들어오는 비중이 매우 크다.
- quarterly path가 `10-Q`와 `Q1/Q2/Q3`만 받으면 Q4-like coverage를 크게 잃는다.

## sample filing observation

`sample_filings` 기준으로 filing timing도 정상적으로 잡힌다.

예: `AAPL`

- `0000320193-26-000006`
  - form: `10-Q`
  - filing_date: `2026-01-30`
  - accepted_at: `2026-01-30 11:01:32`
  - available_at: `2026-01-30 11:01:32`
  - report_date: `2025-12-27`
- `0000320193-25-000079`
  - form: `10-K`
  - filing_date: `2025-10-31`
  - accepted_at: `2025-10-31 10:01:26`
  - available_at: `2025-10-31 10:01:26`
  - report_date: `2025-09-27`

## 결론

Phase 7 reality check 기준으로 late-start의 주원인은 source 부족이 아니었다.

원인 축은 아래였다.

1. quarterly ingestion이 `10-K/FY` rows를 quarterly path에서 제외하고 있었음
2. statement ingestion default period limit이 너무 짧았음
3. quarterly shadow builder가 `report_date`와 `period_end`를 잘못 엮어 valid rows를 버리고 있었음

즉 Phase 7의 실제 수정 포인트는 source 교체가 아니라:

- loader semantics
- ingestion depth
- quarterly shadow normalization

쪽이다.
