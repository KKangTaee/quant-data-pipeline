# Phase 7 Quarterly Rerun Validation

## 목적

- Phase 7 hardening 이후 quarterly strict prototype가 실제로 더 이른 구간부터 열리는지 확인한다.

## validation set

### sample symbols

- `AAPL`
- `MSFT`
- `GOOG`

### managed preset

- `US Statement Coverage 100`

## sample symbol validation

수행:

1. quarterly all-history statement reingest
2. quarterly statement fundamentals shadow rebuild
3. quarterly statement factor shadow rebuild
4. quarterly strict prototype rerun

결과:

- sample raw values:
  - `AAPL`: `2006-09-30 -> 2025-12-27`, `73 periods`
  - `MSFT`: `2007-06-30 -> 2025-12-31`, `87 periods`
  - `GOOG`: `2012-12-31 -> 2025-12-31`, `48 periods`
- sample quarterly shadow:
  - `AAPL`: `73 rows`
  - `MSFT`: `75 rows`
  - `GOOG`: `47 rows`

prototype rerun:

- strategy: `Quality Snapshot (Strict Quarterly Prototype)`
- tickers: `AAPL,MSFT,GOOG`
- start: `2016-01-01`
- end: `2026-03-28`
- result:
  - `first_date = 2016-01-29`
  - `first_active_date = 2016-01-29`

즉 sample-level late-start는 더 이상 `2025` 부근에 묶이지 않았다.

## managed preset validation

rebuild target:

- `US Statement Coverage 100`

결과:

- quarterly raw values:
  - ingest job:
    - `duration_sec = 509.03`
    - `inserted_values = 1,023,285`
  - `100 symbols`
  - `876,657 rows`
  - `min_period_end = 2000-01-01`
  - `max_period_end = 2026-02-28`
  - `distinct_accessions = 6,163`
- quarterly shadow:
  - `100 symbols`
  - `6,796 rows`
  - `min_period_end = 2006-09-24`
  - `max_period_end = 2026-02-28`

prototype rerun:

- strategy: `Quality Snapshot (Strict Quarterly Prototype)`
- preset: `US Statement Coverage 100`
- start: `2016-01-01`
- end: `2026-03-28`
- result:
  - `first_date = 2016-01-29`
  - `first_active_date = 2016-01-29`

## residual notes

- Phase 7 supplementary polish 이후 strict preflight는
  selected end가 주말/휴일이면
  `effective trading end`를 사용해 freshness를 판단한다.
  - 예:
    - selected end `2026-03-28`
    - effective trading end `2026-03-27`
  - 따라서 비거래일 end-date 때문에 whole-universe stale warning이 뜨는 문제는 완화되었다.
- quarterly prototype는 여전히 `research-only` label을 유지한다.
  - 이유:
    - coverage가 개선됐다고 해도 annual strict family만큼 충분히 검증된 public default는 아직 아님

## validation conclusion

Phase 7 first pass 기준:

- quarterly longer-history raw ledger는 복구되었다
- quarterly shadow fundamentals/factors도 기본 preset 범위까지 확장되었다
- quarterly strict prototype의 first active date는 다시 `2016-01-29`까지 당겨졌다

즉 이번 phase의 목적이던
`quarterly strict prototype가 2025 부근에서만 열리는 문제`
는 first-pass 수준에서 해결된 것으로 본다.
