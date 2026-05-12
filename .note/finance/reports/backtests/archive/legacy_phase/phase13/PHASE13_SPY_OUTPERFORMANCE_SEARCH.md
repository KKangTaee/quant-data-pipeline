# PHASE13_SPY_OUTPERFORMANCE_SEARCH

## 목적

사용자가 다음 조건을 만족하는 실전형 포트폴리오를 찾고자 했다.

- 시작일: `2016-01-01`
- 종료일: `2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`
- `SPY`보다 `CAGR`가 높고 `MDD`가 더 좋을 것
- 가능하면 `hold`가 아닌 후보 우선
- family는 `Quality`, `Value`, `Quality + Value` 중에서 더 나은 쪽을 선택 가능

## SPY 기준선

- 구간: `2016-01-04 ~ 2026-04-01`
- `CAGR = 14.0899%`
- `MDD = -33.7172%`

## 탐색 범위

### Quality Strict Annual

- `q_default`
  - `roe`, `roa`, `net_margin`, `asset_turnover`, `current_ratio`
- `q_profitability`
  - `roe`, `roa`, `net_margin`, `operating_margin`, `gross_margin`
- `q_balance_sheet`
  - `current_ratio`, `cash_ratio`, `debt_to_assets`, `debt_ratio`
- `q_capital_discipline`
  - `roe`, `roa`, `cash_ratio`, `debt_to_assets`

### Value Strict Annual

- `v_default`
  - `book_to_market`, `earnings_yield`, `sales_yield`, `ocf_yield`, `operating_income_yield`
- `v_profit_cashflow`
  - `earnings_yield`, `ocf_yield`, `operating_income_yield`, `fcf_yield`
- `v_asset_earnings`
  - `book_to_market`, `earnings_yield`, `operating_income_yield`
- `v_enterprise_cheap`
  - `ev_ebit`, `earnings_yield`, `operating_income_yield`

## 공통 실행 계약

- preset: `US Statement Coverage 100`
- `Universe Contract = Historical Dynamic PIT Universe`
- `min_price = 5.0`
- `min_history_months = 12`
- `min_avg_dollar_volume_20d_m = 5.0`
- `transaction_cost = 10 bps`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`

## 결과

### 1. Value default

- `month_end / interval 1 / top_n 10`
- `CAGR = 18.8054%`
- `MDD = -23.7068%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `rolling = caution`
- `out_of_sample = normal`

### 2. Value default

- `month_end / interval 1 / top_n 5`
- `CAGR = 17.1973%`
- `MDD = -29.6155%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `rolling = caution`
- `out_of_sample = watch`

### 3. Value profit cashflow

- `month_end / interval 1 / top_n 10`
- `CAGR = 14.6085%`
- `MDD = -15.1606%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `rolling = caution`
- `out_of_sample = normal`

## 해석

1. `Quality`만 사용한 탐색은 `SPY`의 CAGR을 넘지 못했다.
2. `Value`만 사용한 탐색은 `SPY`의 CAGR과 MDD를 동시에 넘는 후보가 나왔다.
3. 다만 가장 좋은 후보들도 현재 정책 기준으로는 `hold`가 남았다.

## 결론

이번 조건에서는 `Value Strict Annual` family가 `Quality Strict Annual`보다 더 유망했다.

실전형 후보로는 아래 3개가 우선순위였다.

1. `Value default / month_end / interval 1 / top_n 10`
2. `Value default / month_end / interval 1 / top_n 5`
3. `Value profit cashflow / month_end / interval 1 / top_n 10`

다만 세 후보 모두 `hold`였기 때문에, 현재 구현 범위에서는:

- `SPY` 대비 성과 우위는 확인됨
- `실전 배치 가능` 단계까지는 아직 아님
