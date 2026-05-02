# Phase 4 Strict Annual Shadow Factor Optimization First Pass

## 목적

- `Quality Snapshot (Strict Annual)`의 public 경로를
  raw statement rebuild 반복이 아닌
  precomputed shadow factor history 기반으로 가볍게 만든다.
- 단순히 빠르게만 만드는 것이 아니라,
  sample-universe 기준으로 기존 strict prototype과 같은 전략 의미를 유지하는지 확인한다.

## 문제

- 기존 strict annual public candidate는 사실상
  rebalance date마다 아래를 반복하고 있었다.
  - `nyse_financial_statement_values` read
  - `available_at <= as_of_date` strict filtering
  - statement -> fundamentals 재구성
  - fundamentals -> quality factor 재계산
- `2016-01-01 ~ 2026-03-20`, month-end 기준으로
  rebalance date가 약 `123`개라서,
  wider-universe에서는 체감상 매우 느렸다.

sample top-100 strict snapshot 재구성 단일 호출 시간:
- `2016-01-31`: 약 `3.88s`
- `2020-12-31`: 약 `4.08s`
- `2026-03-20`: 약 `4.19s`

## 구현한 것

### 1. fast public path를 shadow factor snapshot 기반으로 전환

파일:
- `finance/loaders/factors.py`
- `finance/sample.py`
- `app/web/runtime/backtest.py`

핵심:
- `load_statement_factor_snapshot_shadow(...)`
- `get_statement_quality_snapshot_shadow_from_db(...)`
- `run_quality_snapshot_strict_annual_backtest_from_db(...)`

즉 public strict annual path는 이제
`nyse_factors_statement` history를 한 번 읽고,
in-memory as-of snapshot map을 만들어 전략을 실행한다.

### 2. annual shadow history 의미 보정

초기 shadow path는 두 가지 문제가 있었다.

1. annual history에 quarter-like row가 섞였다
- 원인:
  - annual statement values 안에 10-K comparative fact가 섞여 있었는데,
    shadow fundamentals rebuild가 raw `period_end` 기준으로 그대로 row를 만들었다.
- 보정:
  - `report_date` anchor를 이용해 실제 reported annual period만 shadow history에 남긴다.

2. `period_end`별로 너무 늦은 availability를 잡았다
- 원인:
  - 같은 `period_end`에 대해 later filing/restatement가 덮어쓰면서
    `latest_available_for_period_end` 의미가 되었다.
- 보정:
  - coherent earliest filing snapshot을 사용하도록 바꾸고,
    timing basis를 `first_available_for_period_end`로 정리했다.

파일:
- `finance/data/fundamentals.py`

## 검증

### sample-universe parity

대상:
- `AAPL`, `MSFT`, `GOOG`
- `2016-01-01 ~ 2026-03-20`
- month-end

결과:
- optimized strict public path:
  - elapsed: `0.331s`
  - `End Balance = 93934.6`
  - first active date: `2016-01-29`
- prototype rebuild path:
  - elapsed: `17.09s`
  - `End Balance = 93934.6`
  - first active date: `2016-01-29`

즉 sample-universe 기준으로:
- 속도는 크게 개선되었고
- 결과는 prototype과 일치한다

### wider-universe runtime check

대상:
- `US Statement Coverage 100`
- `Quality Snapshot (Strict Annual)`
- `top_n = 10`

결과:
- elapsed: `3.381s`
- `End Balance = 20198.7`
- first active date: `2021-04-30`

## 현재 의미

- strict annual public candidate는 이제
  raw statement rebuild 검증용 경로가 아니라,
  shadow factor history를 쓰는 실제 product-facing fast path가 되었다.
- prototype rebuild path는 계속 남겨두되,
  parity 기준과 architecture validation 용도로 보는 편이 맞다.
