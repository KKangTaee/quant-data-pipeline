# Phase 7 Raw Statement Ledger Review And Decision

## 리뷰 대상

- `finance_fundamental.nyse_financial_statement_filings`
- `finance_fundamental.nyse_financial_statement_values`
- `finance_fundamental.nyse_financial_statement_labels`

## 결론

이번 Phase 7 first pass에서는 raw statement ledger를 대대적으로 재생성하지 않았다.

결정:

- `keep tables`
- `patch loader semantics`
- `patch quarterly shadow semantics`

즉 late-start의 주원인은 schema 부재보다 **수집/정규화 규칙**에 있었다.

## 왜 유지 결정을 했는가

현재 raw ledger는 이미 핵심 PIT field를 담고 있었다.

`nyse_financial_statement_filings`

- `accession_no`
- `form_type`
- `filing_date`
- `accepted_at`
- `available_at`
- `report_date`

`nyse_financial_statement_values`

- `period_start`
- `period_end`
- `period_label`
- `period_type`
- `source_period_type`
- `fiscal_year`
- `fiscal_period`
- `fiscal_quarter`
- `statement_type`
- `concept`
- `unit`
- `filing_date`
- `accepted_at`
- `available_at`
- `report_date`
- `form_type`
- `accession_no`

즉 raw ledger의 표현력 자체는 이미 PIT-friendly 방향에 충분히 가까웠다.

## 실제 blocker

실제 blocker는 아래였다.

1. quarterly path가 `10-Q/Q1/Q2/Q3`만 허용
2. statement ingestion default `periods`가 너무 짧음
3. shadow fundamentals builder가 `report_date == period_end`에 가까운 잘못된 anchor filter를 적용

이 세 가지 때문에:

- source에는 오래된 fact가 있어도
- DB에는 최근 몇 개 period만 들어오고
- 들어온 row 중 일부도 shadow build에서 버려졌다

## destructive redesign을 보류한 이유

이번 시점에서 table drop/recreate를 하지 않은 이유:

- 현재 table이 이미 PIT timing field를 담고 있음
- late-start는 구조 자체보다 loader behavior 문제였음
- 우선 semantics fix만으로 quarterly recovery가 실제로 가능한지 검증하는 편이 리스크가 낮음

## human-readable inspection path

이번 phase에서 사람이 확인하기 쉬운 inspection path를 같이 정리했다.

### 1. source payload reality check

- `finance.data.financial_statements.inspect_financial_statement_source(symbol, sample_size=...)`

역할:

- source fact count
- filing count
- form / fiscal-period 분포
- timing field inventory
- sample facts / sample filings

### 2. DB timing audit

- `finance.loaders.load_statement_timing_audit(...)`

역할:

- `period_start`
- `period_end`
- `fiscal_period`
- `filing_date`
- `accepted_at`
- `available_at`
- `report_date`
- `form_type`
- `accession_no`

를 row 단위로 바로 비교 확인

### 3. DB coverage summary

- `finance.loaders.load_statement_coverage_summary(...)`

역할:

- symbol별:
  - `distinct_accessions`
  - `distinct_period_ends`
  - `min_period_end`
  - `max_period_end`
  - `min_available_at`
  - `max_available_at`

를 빠르게 확인

## Phase 7 decision

이번 first pass의 raw ledger decision은 다음과 같다.

- schema는 유지
- source inspection helper 강화
- timing audit loader 추가
- quarterly ingestion semantics 수정
- quarterly shadow normalization 수정

즉 raw ledger는 유지하되, **더 정확히 읽고 더 깊게 적재하는 방향**으로 정리했다.
