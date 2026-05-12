# PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH

## 목적

`Quality Strict Annual` family만 대상으로, 다음 조건을 만족하는 후보를 찾는다.

- 시작일: `2016-01-01`
- 종료일: `2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`
- `SPY`보다
  - `CAGR`이 높고
  - `MDD`가 더 좋다
- 가능하면 `hold`가 아닌 후보를 우선한다

## SPY 기준선

동일 기간에서 `SPY` baseline은 다음과 같다.

- `Start Date = 2016-01-04`
- `CAGR = 14.09%`
- `Maximum Drawdown = -33.72%`

## 탐색 방식

### 1차 스크리닝

먼저 `Quality Snapshot (Strict Annual)`만 사용해서 다음 factor set을 비교했다.

- `default`
  - `roe`, `roa`, `net_margin`, `asset_turnover`, `current_ratio`
- `legacy`
  - `roe`, `gross_margin`, `operating_margin`, `debt_ratio`
- `profitability`
  - `roe`, `roa`, `net_margin`, `operating_margin`, `gross_margin`
- `balance_sheet`
  - `current_ratio`, `cash_ratio`, `debt_to_assets`, `debt_ratio`
- `capital_discipline`
  - `roe`, `roa`, `cash_ratio`, `debt_to_assets`
- `efficiency`
  - `asset_turnover`, `operating_margin`, `gross_margin`, `net_margin`

스크리닝 설정:

- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 2 / 5 / 10`
- `trend_filter = off`
- `market_regime = off`
- `underperformance_guardrail = off`
- `drawdown_guardrail = off`
- `benchmark = SPY`

### 2차 검증

1차 스크리닝에서 SPY를 이긴 후보들을 대상으로 다음 조합을 다시 확인했다.

- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = off`
- `drawdown_guardrail = off`

이 조합은 실전형 UI 설정에 더 가깝고, raw performance와 risk overlay의 균형을 같이 볼 수 있다.

## 최종 후보

### 1. `capital_discipline`

- quality factors:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 10`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = off`
- `drawdown_guardrail = off`
- `benchmark = SPY`
- 결과:
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`
  - `validation = caution`
  - `rolling = normal`
  - `out_of_sample = normal`
  - `CAGR = 15.80%`
  - `MDD = -27.97%`

### 2. `balance_sheet`

- quality factors:
  - `current_ratio`
  - `cash_ratio`
  - `debt_to_assets`
  - `debt_ratio`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 5`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = off`
- `drawdown_guardrail = off`
- `benchmark = SPY`
- 결과:
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`
  - `validation = caution`
  - `rolling = normal`
  - `out_of_sample = normal`
  - `CAGR = 15.71%`
  - `MDD = -33.20%`

### 3. `balance_sheet`

- quality factors:
  - `current_ratio`
  - `cash_ratio`
  - `debt_to_assets`
  - `debt_ratio`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 10`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = off`
- `drawdown_guardrail = off`
- `benchmark = SPY`
- 결과:
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`
  - `validation = caution`
  - `rolling = normal`
  - `out_of_sample = normal`
  - `CAGR = 14.46%`
  - `MDD = -26.83%`

## 해석

이 탐색에서 확인된 핵심은 다음과 같다.

1. `Quality Strict Annual`에서도 `SPY`를 동시에 이기는 후보는 존재한다.
2. 다만 현재 real-money hardening을 전부 켜면, 그 edge가 크게 약해진다.
3. 즉 `Quality` family는 raw return 측면에서는 `SPY`를 이길 수 있지만,
   운영 계약까지 완전히 넣으면 아직 `hold`에 가까운 해석이 남는다.

## 실무 메모

- `capital_discipline` top 10은 가장 높은 CAGR을 보였다.
- `balance_sheet` top 5는 `SPY` 대비 drawdown 방어가 가장 덜 무너진 편이었다.
- `balance_sheet` top 10은 `SPY`를 가장 안전하게 넘는 쪽에 가까웠다.

## 후속 판단

이 family는 지금 상태에서 다음 둘 중 하나로 읽는 것이 맞다.

1. raw return reference로는 충분히 `SPY`를 넘길 수 있는 후보가 있다.
2. 하지만 full hardening까지 포함한 실전형 candidate로는 아직 추가 검증이 필요하다.
