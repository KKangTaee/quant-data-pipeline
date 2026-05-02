# Phase 4 Annual Statement Period Limit Fix And Coverage Expansion

## 배경

- 사용자가 `Extended Statement Refresh`를
  - `annual, periods=12`
  - `quarterly, periods=12`
  로 실행한 뒤,
  sample universe(`AAPL`, `MSFT`, `GOOG`)의 strict statement coverage를 다시 확인했다.
- 그 결과 `annual` coverage는 여전히 너무 짧았고,
  특히 `MSFT`는 `2023-12-31` 이후만 남아 있어
  statement-driven quality long-history backtest를 막고 있었다.

## 핵심 원인

- 원천 source 자체가 짧은 것이 아니었다.
- `finance.data.financial_statements._iter_value_rows_from_source(...)`가
  `periods=N` 제한을 걸 때
  raw row-level `period_end` 기준으로 latest N period bucket을 고르고 있었다.
- annual 10-K fact 안에는 quarter-end처럼 보이는 `period_end`가 함께 섞여 들어오는 경우가 있고,
  이 값들이 최신 annual report들을 crowd out 하면서
  older true annual coverage가 잘려 나가고 있었다.

예시:
- fix 이전 `MSFT annual` strict coverage:
  - `min_period_end = 2023-12-31`
  - `max_period_end = 2025-06-30`
- source inspection 기준 latest reported annual periods:
  - `2025-06-30`
  - `2024-06-30`
  - `2023-06-30`
  - `2022-06-30`
  - ...
  - `2014-06-30`

즉 source는 깊었지만, collector slicing semantics가 annual reported-period 의미와 맞지 않았다.

## 구현한 수정

### 1. annual/quarterly period slicing 기준 변경

대상:
- `finance.data.financial_statements._iter_value_rows_from_source(...)`

변경:
- `periods=N` 제한을 raw `period_end` bucket이 아니라
  `report_date` 우선, 없으면 `period_end` fallback인
  reported-period 기준으로 잡도록 수정했다.
- 결과적으로 annual refresh는
  "latest N raw period_end facts"가 아니라
  "latest N reported annual periods" 의미로 동작하게 되었다.

### 2. financial statements canonical refresh 추가

대상:
- `finance.data.financial_statements.upsert_financial_statements(...)`

변경:
- `replace_symbol_history=True` 기본값을 추가했다.
- successful symbol/freq scope에 대해:
  - `nyse_financial_statement_values`
    - `symbol + freq`
  - `nyse_financial_statement_labels`
    - `symbol + as_of_period_type`
  를 먼저 delete 한 뒤 다시 insert/upsert 하도록 바꿨다.

의미:
- old slicing semantics로 이미 들어가 있던 row를 남겨두지 않고,
  latest N reported periods 기준 canonical history로 교체한다.

## 재실행

sample universe annual refresh 재실행:
- `AAPL`
- `MSFT`
- `GOOG`
- `freq='annual'`
- `periods=12`

결과:
- `inserted_values = 7176`
- `upserted_labels = 3198`
- `failed_symbols = []`

## 수정 후 coverage 결과

strict annual coverage summary:

- `AAPL`
  - `strict_rows = 2382`
  - `distinct_accessions = 12`
  - `min_period_end = 2011-09-24`
  - `max_period_end = 2025-09-27`
  - `min_available_at = 2014-10-27 21:11:55`
- `GOOG`
  - `strict_rows = 1995`
  - `distinct_accessions = 11`
  - `min_period_end = 2012-12-31`
  - `max_period_end = 2025-12-31`
  - `min_available_at = 2016-02-11 21:38:35`
- `MSFT`
  - `strict_rows = 2608`
  - `distinct_accessions = 12`
  - `min_period_end = 2011-06-30`
  - `max_period_end = 2025-06-30`
  - `min_available_at = 2014-07-31 21:16:52`

핵심 변화:
- annual strict statement history가 이제 sample universe 기준으로
  대략 `2011~2012` 수준까지 열린다.

## shadow rebuild 결과

annual shadow rebuild:
- fundamentals rows written: `92`
- factors rows written: `92`
- shadow factor `period_end` 범위:
  - `2011-06-30 ~ 2025-12-31`
- `market_cap_non_null = 12`

## statement-driven quality prototype 재검증

입력:
- `start = 2016-01-01`
- `end = 2026-03-20`
- `statement_freq = 'annual'`
- `tickers = ['AAPL', 'MSFT', 'GOOG']`
- `top_n = 2`
- `rebalance_interval = 1`

결과:
- `first_active = 2016-02-29`
- `End Balance = 93934.6`
- `CAGR = 0.24725673938829384`
- `Sharpe Ratio = 0.3260280474048049`
- `Maximum Drawdown = -0.3348712082563604`

## 현재 판단

- sample universe 기준으로는
  annual strict statement-driven quality path가 이제
  `2016` 시작 long-history backtest를 실제로 지원한다.
- 따라서 이전 blocker였던
  "annual strict statement coverage가 너무 짧다"
  는 sample-universe 기준으로는 해소되었다.
- 다음 판단 축은:
  - 이 annual strict statement path를 public 후보로 더 키울지
  - 아니면 wider universe coverage를 먼저 늘릴지
  로 옮겨간 상태다.
