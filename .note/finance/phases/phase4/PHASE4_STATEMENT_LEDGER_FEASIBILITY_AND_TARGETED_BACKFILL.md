# Phase 4 Statement Ledger Feasibility And Targeted Backfill

## 목적
이 문서는 `statement-driven quality path`로 가기 전에

1. small feasibility test를 먼저 수행하고
2. 같은 샘플 유니버스에 대해 targeted statement backfill까지 진행한

결과를 정리한다.

대상 샘플 유니버스:
- `AAPL`
- `MSFT`
- `GOOG`

## 실행한 것

### feasibility test

다음 job을 직접 실행했다.

- `run_extended_statement_refresh(['AAPL','MSFT','GOOG'], freq='annual', periods=12, period='annual')`
- `run_extended_statement_refresh(['AAPL','MSFT','GOOG'], freq='quarterly', periods=12, period='quarterly')`

결과:

- annual
  - `status = success`
  - `duration_sec = 36.348`
  - `rows_written = 1407`
- quarterly
  - `status = success`
  - `duration_sec = 7.296`
  - `rows_written = 1545`

즉 current EDGAR-based detailed statement path는
적어도 sample universe 수준에서는 정상적으로 확장 수집이 가능했다.

### targeted backfill

위 feasibility test 자체가 곧 targeted backfill 역할을 수행했다.

즉 현재 local ledger는
sample universe 기준으로
기존보다 더 긴 statement history를 확보한 상태다.

## backfill 후 확인한 coverage

### `nyse_financial_statement_values`

- `AAPL`
  - annual: `2021-09-25 ~ 2025-09-27`
  - quarterly: `2024-09-28 ~ 2025-12-27`
- `GOOG`
  - annual: `2021-12-31 ~ 2025-12-31`
  - quarterly: `2024-06-30 ~ 2025-09-30`
- `MSFT`
  - annual: `2023-12-31 ~ 2025-06-30`
  - quarterly: `2024-09-30 ~ 2025-12-31`

### strict snapshot check

`load_statement_snapshot_strict(...)`로 annual strict snapshot을 확인했을 때:

- `2016-01-31 ~ 2022-01-31`: empty
- `2023-01-31`: `AAPL` only

즉 targeted backfill은 실제로 history를 늘렸지만,
아직 `2016` 시작 quality strategy를 열 수준의 coverage는 아니다.

## 해석

이번 결과는 두 가지를 뜻한다.

1. `option 2` 방향은 실행 가능하다
   - statement ledger 기반 확장은 현실적인 경로다
2. 하지만 아직 depth가 충분하지 않다
   - sample universe에서도 earliest usable annual coverage가 대체로 `2021~2023`
   - 따라서 `2016` 시작 quality backtest를 바로 여는 데는 아직 부족하다

## 결론

이번 작업으로:

- feasibility test는 성공
- sample universe targeted backfill도 성공

상태가 되었다.

하지만 다음 product decision은 여전히 필요하다.

1. 더 넓은 universe / 더 긴 history backfill을 계속할지
2. public quality 전략은 현재 broad-research path를 유지할지
3. statement-driven quality는 `2021+` 또는 `2023+` 구간용으로 먼저 실험할지
