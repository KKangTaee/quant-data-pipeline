# PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH

## 목적

`2016-01-01 ~ 2026-04-01` 구간에서 다음 조건을 동시에 만족하는 실전형 후보를 찾기 위해 `Quality`, `Value`, `Quality + Value` strict annual family를 다시 탐색했다.

- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`
- `CAGR >= 15%`
- `Maximum Drawdown >= -20%`

이 탐색은 `SPY`를 단순 비교 기준으로 두고, `SPY`보다 더 나은 위험/수익 구조를 찾는 데도 초점을 맞췄다.

## SPY 기준선

SPY 자체 기준은 다음과 같이 잡았다.

- 시작일: `2016-01-04`
- 종료일: `2026-04-01`
- `CAGR = 14.09%`
- `MDD = -33.72%`

## 탐색 범위

### Quality Strict Annual

Quality family는 `SPY` 대비 CAGR과 MDD를 둘 다 넘는 후보를 찾긴 했지만, full hardening 기준에서는 `hold`를 벗어나지 못했다.

대표 후보:

- `capital_discipline`
  - factors: `roe, roa, cash_ratio, debt_to_assets`
  - `month_end`, `rebalance_interval=1`, `top_n=10`
  - `CAGR 15.80%`
  - `MDD -27.97%`
  - `promotion = hold`

### Value Strict Annual

Value family는 이번 탐색에서 가장 강했다.

대표 후보:

- `v_default`
  - factors: `book_to_market, earnings_yield, sales_yield, ocf_yield, operating_income_yield`
  - `month_end`, `rebalance_interval=1`, `top_n=10`
  - `trend_filter=off`, `market_regime=off`
  - `CAGR 29.89%`
  - `MDD -29.15%`
  - `promotion = real_money_candidate`

- `v_profit_cashflow`
  - factors: `earnings_yield, ocf_yield, operating_income_yield, fcf_yield`
  - `month_end`, `rebalance_interval=1`, `top_n=10`
  - `benchmark = SPY`
  - `trend_filter=on`, `market_regime=on`
  - `CAGR 14.61%`
  - `MDD -15.16%`
  - `promotion = hold`

- `v_profit_cashflow`
  - same factor set
  - `benchmark = LQD`
  - `month_end`, `rebalance_interval=1`, `top_n=5`
  - `CAGR 13.16%`
  - `MDD -19.18%`
  - `promotion = hold`

### Quality + Value Strict Annual

Quality + Value family는 이번 조건에서 가장 보수적으로 움직였고, drawdown은 줄일 수 있었지만 CAGR이 너무 약해지는 경우가 많았다.

대표 near-miss:

- `q_balance_sheet + v_cashflow_only`
  - `month_end`, `rebalance_interval=6`, `top_n=30`
  - `CAGR 2.40%`
  - `MDD -13.57%`
  - `promotion = hold`

## 결론

이번 탐색 범위에서는 다음 조건을 동시에 만족하는 후보를 찾지 못했다.

- `CAGR >= 15%`
- `Maximum Drawdown >= -20%`
- `top_n <= 10`
- `Historical Dynamic PIT Universe`

정리하면:

1. `Value Strict Annual`이 성과 기준으로는 가장 강했다.
2. `Quality Strict Annual`은 `SPY`를 넘는 후보는 있었지만 hardening 기준에서 여전히 `hold`가 남았다.
3. `Quality + Value`는 `MDD`를 낮출 수는 있었지만 `CAGR`가 너무 약해졌다.

## 실무 해석

현재 구현과 UI-reproducible 설정 범위에서는 `SPY`를 안정적으로 이기는 후보는 찾았지만, `CAGR >= 15%`와 `MDD >= -20%`를 동시에 만족하는 조합은 없었다.

따라서 다음 실무 선택지는 둘 중 하나다.

1. `MDD` 기준을 `25%` 근처로 완화한다.
2. `CAGR / MDD`가 아니라 `hold` 여부까지 포함한 deployment-readiness 기준으로 다시 좁힌다.
