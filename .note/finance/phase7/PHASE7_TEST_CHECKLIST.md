# Phase 7 Test Checklist

## 목적

- statement PIT hardening과 quarterly coverage recovery가 실제로 UI/DB 기준으로 반영됐는지 확인한다.

## 1. Statement Ingestion UI

- `Ingestion > Extended Statement Refresh`
  - `Extended Statement Periods`가 `0`부터 입력 가능한지 확인
  - help/caption에 `0 = all available periods`가 보이는지 확인
- `Ingestion > Financial Statement Ingestion`
  - `Financial Statement Periods`가 `0`부터 입력 가능한지 확인
  - help/caption에 `0 = all available periods`가 보이는지 확인

## 2. Quarterly Raw Ledger Coverage

- 우선 추천:
  - `Ingestion > Statement PIT Inspection`
  - symbols: `AAPL,MSFT,GOOG`
  - freq: `quarterly`
  - `Run Statement PIT Inspection`
  - `Coverage Summary`에서 min/max period 확인

- Python or notebook으로도 아래 확인 가능

```python
from finance.loaders import load_statement_coverage_summary
print(load_statement_coverage_summary(symbols=["AAPL", "MSFT", "GOOG"], freq="quarterly"))
```

기대:

- `AAPL` min period가 `2006`대로 내려가 있음
- `MSFT` min period가 `2007`대로 내려가 있음
- `GOOG` min period가 `2012`대로 내려가 있음

## 3. Timing Audit Helper

- 우선 추천:
  - `Ingestion > Statement PIT Inspection`
  - 같은 입력으로 실행
  - `Timing Audit` 표에서 PIT timing 컬럼 확인

- Python or notebook으로도 아래 확인 가능

```python
from finance.loaders import load_statement_timing_audit
df = load_statement_timing_audit(symbols=["AAPL"], freq="quarterly", limit_per_symbol=5)
print(df)
```

기대:

- 다음 컬럼이 보임
  - `period_start`
  - `period_end`
  - `fiscal_period`
  - `filing_date`
  - `accepted_at`
  - `available_at`
  - `report_date`
  - `form_type`
  - `accession_no`

## 4. Source Inspection Helper

- 우선 추천:
  - `Ingestion > Statement PIT Inspection`
  - `Source Inspection Symbol = AAPL`
  - `Source Payload Inspection` 섹션 확인

- Python or notebook으로도 아래 확인 가능

```python
from finance.data.financial_statements import inspect_financial_statement_source
print(inspect_financial_statement_source("AAPL", sample_size=2))
```

기대:

- 아래 항목이 보임
  - `fiscal_period_counts`
  - `timing_field_inventory`
  - `sample_filings`

## 5. Quarterly Prototype Smoke Test

- `Backtest > Single Strategy`
- `Quality Snapshot (Strict Quarterly Prototype)`
- preset: `US Statement Coverage 100`
- start: `2016-01-01`
- end: today

확인 포인트:

- 더 이상 active period가 `2025`부터만 열리지 않는지
- equity curve가 `2016`부터 실제로 움직이는지
- `Selection History`가 보이는지
- `Statement Shadow Coverage Preview`가 보이는지
  - `Earliest Period`가 `2000s` / `2010s` 초반 구간으로 열려 있는지
- end가 비거래일일 때
  - `Price Freshness Preflight`가 `effective trading end`를 보여주고
  - whole-universe stale warning으로 오해를 만들지 않는지

정상 기대:

- `first active date`가 `2016-01-29` 부근

## 6. Quarterly Prototype Manual Ticker Test

- `Quality Snapshot (Strict Quarterly Prototype)`
- tickers:
  - `AAPL,MSFT,GOOG`
- start: `2016-01-01`
- end: today

확인 포인트:

- `2016`부터 active하게 동작하는지
- 초기 수년이 전부 flat cash-only 상태가 아닌지

## 7. Shadow Coverage Check

- Python or notebook에서 아래 확인

```python
from finance.data.db.mysql import MySQLClient
db = MySQLClient("localhost", "root", "1234", 3306)
db.use_db("finance_fundamental")
rows = db.query(
    """
    SELECT COUNT(DISTINCT symbol) AS symbols_done,
           MIN(period_end) AS min_period_end,
           MAX(period_end) AS max_period_end,
           COUNT(*) AS row_count
    FROM nyse_fundamentals_statement
    WHERE freq='quarterly'
    """
)
print(rows)
db.close()
```

기대:

- quarterly shadow가 최근 6 row 수준에 머무르지 않고 longer-history row를 갖고 있어야 함

## 8. Regression Check

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`

확인 포인트:

- annual strict family 동작이 깨지지 않았는지
- strict annual history / interpretation / compare 흐름이 그대로인지

## 권장 순서

1. ingestion UI에서 `0 = all available` 입력 확인
2. sample symbol coverage summary 확인
3. quarterly prototype manual ticker test
4. quarterly prototype `US Statement Coverage 100` test
5. quarterly shadow coverage preview / effective trading end 확인
6. annual strict regression 확인
