# Phase 4 Strict Annual Wider Universe Stage 3 Current DB Audit

> 참고:
> 이 문서는 wider-universe stage 3의 당시 DB 상태를 기록한 audit 문서다.
> 이후 closeout 단계에서
> `US Statement Coverage 500/1000`의 coverage는 더 올라갔고,
> `Value Snapshot (Strict Annual)`도
> `2016-01-29`부터 active하게 동작하도록 회복되었다.
> 최신 closeout 판단은
> `.note/finance/phases/phase4/PHASE4_COVERAGE1000_AND_VALUE_STRICT_CLOSEOUT.md`
> 를 기준으로 보는 편이 정확하다.

## 목적

- `US Statement Coverage 300` 다음 단계로 `500`, `1000` preset을 평가한다.
- 먼저 current DB 상태에서 strict annual family가 어디까지 usable한지 확인한다.

## 기준 universe

- source:
  - `finance_meta.nyse_asset_profile`
- filter:
  - `kind='stock'`
  - `country='United States'`
  - profile filter enabled
- ranking:
  - `market_cap DESC`

## current DB audit 결과

### Profile universe counts

- `Profile Filtered Stocks` total:
  - `5783`
- `Profile Filtered Stocks / United States`:
  - `4441`
- `Profile Filtered Stocks / Non-US`:
  - `1094`

### `US Statement Coverage 500`

- strict annual coverage:
  - covered symbols: `396 / 500`
  - `12+` accessions: `327`
  - `8+` accessions: `352`
- price freshness:
  - common latest: `2026-03-17`
  - newest latest: `2026-03-20`
  - spread: `3d`
- quality strict:
  - first active date: `2016-01-29`
  - rows: `124`
  - `End Balance = 196548.1`
  - `CAGR = 34.15%`
  - `Sharpe Ratio = 1.3369`
  - `Maximum Drawdown = -31.56%`
- value strict:
  - first active date: `2021-08-31`
  - rows: `124`
  - `End Balance = 21112.5`
  - `CAGR = 7.65%`
  - `Sharpe Ratio = 0.5692`
  - `Maximum Drawdown = -27.78%`

### `US Statement Coverage 1000`

- strict annual coverage:
  - covered symbols: `396 / 1000`
  - `12+` accessions: `327`
  - `8+` accessions: `352`
- price freshness:
  - common latest: `2026-01-30`
  - newest latest: `2026-03-20`
  - spread: `49d`
- quality strict:
  - first active date: `2016-01-29`
  - rows: `125`
  - `End Balance = 184685.5`
  - `CAGR = 33.33%`
  - `Sharpe Ratio = 1.3057`
  - `Maximum Drawdown = -31.56%`
- value strict:
  - first active date: `2021-08-31`
  - rows: `125`
  - `End Balance = 20165.2`
  - `CAGR = 7.16%`
  - `Sharpe Ratio = 0.5378`
  - `Maximum Drawdown = -27.78%`

## 해석

- current DB 상태에서는 `500`, `1000` 모두 아직 wider-universe operator preset 수준이다.
- 핵심 병목은
  - statement coverage completeness
  - latest price freshness spread
  두 가지다.
- 특히 `1000`은 common latest가 `2026-01-30`이라서 public default로 쓰기엔 아직 이르다.
