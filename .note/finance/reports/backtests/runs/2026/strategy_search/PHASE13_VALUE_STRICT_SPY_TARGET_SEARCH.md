# PHASE13_VALUE_STRICT_SPY_TARGET_SEARCH

## 목적

사용자가 다음 조건을 만족하는 포트폴리오를 찾도록 요청했다.

- 기간: `2016-01-01 ~ 2026-04-01`
- universe contract: `Historical Dynamic PIT Universe`
- 비교 기준: `SPY`
- 목표:
  - `CAGR >= 15%`
  - `Maximum Drawdown >= -20%`
- `top_n <= 10`

이번 탐색은 `Quality`, `Value`, `Quality + Value` family를 병렬로 살펴봤고, 최종적으로 `Value Strict Annual`에서 만족 후보를 찾았다.

## SPY 기준선

- `SPY CAGR = 14.09%`
- `SPY MDD = -33.72%`

## 최종 후보

### Value Strict Annual

- factor set:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `Universe Contract = Historical Dynamic PIT Universe`
- `start = 2016-01-01`
- `end = 2026-04-01`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 9`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`

### 결과

- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `rolling = caution`
- `out_of_sample = caution`
- `CAGR = 15.84%`
- `MDD = -17.42%`

## 근접 후보

### 같은 factor set, `top_n = 7`

- `CAGR = 15.24%`
- `MDD = -19.57%`
- 상태:
  - `hold`

### 같은 factor set, `top_n = 10`

- `CAGR = 14.61%`
- `MDD = -15.16%`
- 상태:
  - `hold`

## 해석

이번 목표는 숫자 기준만 보면 충족하는 후보가 하나 나왔다.

- `SPY`보다 `CAGR`이 높다.
- `SPY`보다 `MDD`가 낮다.
- `top_n <= 10` 조건도 지킨다.

다만 승격 계약 관점에서는 아직 `hold`다.
즉 이 후보는:

- 성과 비교용 레퍼런스
- 실전형 운용 후보의 강한 near-final example

으로 보는 것이 맞다.

## 실무적 의미

`Value Strict Annual`의 다음은 두 가지다.

1. 지금 후보를 그대로 참고용으로 사용한다.
2. `hold`를 풀기 위해 benchmark / policy contract를 조금 더 완화한 버전을 찾는다.

현재까지는 이 후보가 가장 균형이 좋다.
