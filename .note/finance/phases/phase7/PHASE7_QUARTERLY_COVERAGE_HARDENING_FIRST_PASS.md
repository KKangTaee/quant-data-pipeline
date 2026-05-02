# Phase 7 Quarterly Coverage Hardening First Pass

## 목표

- quarterly strict prototype가 `2025` 부근에서만 열리던 문제를 데이터/loader 레벨에서 완화한다.
- source truth는 유지하면서 quarterly longer-history를 shadow path로 연결한다.

## 코드 변경

### 1. quarterly ingestion이 `10-K/FY`를 포함하도록 수정

파일:

- `finance/data/financial_statements.py`

변경:

- quarterly allowed forms:
  - 기존: `10-Q`, `10-Q/A`
  - 변경: `10-Q`, `10-Q/A`, `10-K`, `10-K/A`
- quarterly allowed fiscal periods:
  - 기존: `Q1`, `Q2`, `Q3`
  - 변경: `Q1`, `Q2`, `Q3`, `FY`

의미:

- EDGAR에서 Q4-like year-end quarter가 `10-K` + `FY`로 잡히는 케이스를 quarterly path가 더 이상 버리지 않음

### 2. statement ingestion에 all-history 모드 추가

파일:

- `finance/data/financial_statements.py`
- `app/jobs/ingestion_jobs.py`
- `app/web/streamlit_app.py`

변경:

- `periods=0`을 공식적으로 허용
- 의미:
  - `0 = all available periods`
- UI number input:
  - 기존: `min=1`, `max=12`
  - 변경: `min=0`, `max=80`
- manual / extended statement job 둘 다 help/caption 추가

의미:

- quarterly recovery나 PIT hardening 때는 이제 더 이상 `4` 또는 `8` period에 갇히지 않음

### 3. quarterly shadow builder의 잘못된 report-date anchor 제거

파일:

- `finance/data/fundamentals.py`

기존 문제:

- `build_fundamentals_history_from_statement_values()`에서
  `report_date` set에 `period_end`가 직접 포함되는 row만 남기려는 filter가 있었다
- quarterly filings는 comparative prior-period facts를 포함하기 때문에
  이 조건이 valid quarterly rows를 대량으로 버렸다

수정:

- 해당 filter 제거
- shadow builder는 이제
  - `symbol + period_end`
  - earliest usable `available_at`
기준 snapshot 구성에 집중

의미:

- quarterly raw row가 shadow fundamentals/factors로 정상적으로 전달됨

### 4. operator inspection helper 강화

파일:

- `finance/data/financial_statements.py`
- `finance/loaders/financial_statements.py`
- `finance/loaders/__init__.py`

추가:

- `inspect_financial_statement_source()` 출력 강화
  - `fiscal_period_counts`
  - `timing_field_inventory`
  - `sample_filings`
- `load_statement_timing_audit(...)` 추가

## before / after 핵심 수치

### source-level quarterly period recovery

sample symbols:

- `AAPL`
  - before-like limited path: `distinct_periods4 = 11`
  - all available path: `distinct_periods0 = 73`
- `MSFT`
  - before-like limited path: `15`
  - all available path: `87`
- `GOOG`
  - before-like limited path: `10`
  - all available path: `48`

### DB quarterly raw values

sample symbols reingest 후:

- `AAPL`
  - before: `min_period_end = 2024-09-28`, `distinct_period_ends = 6`
  - after: `min_period_end = 2006-09-30`, `distinct_period_ends = 73`
- `MSFT`
  - before: `2024-09-30`, `6`
  - after: `2007-06-30`, `87`
- `GOOG`
  - before: `2024-06-30`, `6`
  - after: `2012-12-31`, `48`

### `US Statement Coverage 100` quarterly ledger

quarterly all-history rebuild 후:

- ingest job result:
  - duration: `509.03s`
  - `inserted_values = 1,023,285`
- `symbols_done = 100`
- `min_period_end = 2000-01-01`
- `max_period_end = 2026-02-28`
- `row_count = 876,657`
- `distinct_accessions = 6,163`

### `US Statement Coverage 100` quarterly shadow

shadow rebuild 후:

- `symbols_done = 100`
- `min_period_end = 2006-09-24`
- `max_period_end = 2026-02-28`
- `row_count = 6,796`

## 결론

Phase 7 first pass 기준 quarterly late-start의 핵심 원인은 다음으로 고정된다.

1. quarterly path가 year-end `10-K/FY` rows를 버림
2. ingestion depth가 너무 짧음
3. shadow builder가 `report_date` semantics를 잘못 적용함

이번 패치로 raw ledger와 shadow path 모두 longer-history quarterly 경로를 다시 열었다.
