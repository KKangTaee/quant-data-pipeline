# PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH

## 목적

사용자가 다음 요청을 했다.

- `hold`가 왜 나는지 파악
- 그 `hold`를 해결한 상태에서
- `CAGR >= 15%` and `MDD >= -20%`
- 가능하면 `hold`가 아닌 상태의 후보를 찾기

고정 조건은 다음과 같다.

- `start = 2016-01-01`
- `end = 2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`

## 1. hold 원인

가장 먼저 확인한 exact-hit 후보는 `Value Strict Annual`이었다.

### 확인한 설정

- `Value > Strict Annual`
- factor:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 9`
- benchmark: `SPY`
- `Trend Filter = on`
- `Market Regime = on`
- `Underperformance Guardrail = on`
- `Drawdown Guardrail = on`

### 결과

- `CAGR = 15.84%`
- `MDD = -17.42%`
- `promotion_decision = hold`
- `shortlist_status = hold`
- `deployment_readiness_status = blocked`

### hold 원인

메인 환경에서 확인한 결과, hold의 직접 원인은 다음이었다.

- `validation_status = caution`
- `validation_policy_status = caution`

관련 메타도 함께 확인했다.

- `rolling_review_status = caution`
- `promotion_rationale = ['validation_caution', 'validation_policy_caution']`
- `promotion_next_step = resolve_validation_gaps_before_promotion`
- `rolling_underperformance_share = 0.36607142857142855`
- `rolling_underperformance_worst_excess_return = -0.3938795612089725`

즉, 성과 숫자는 목표에 가까웠지만, 최근 구간/정책 검증이 아직 보수적으로 남아서 `hold`가 걸렸다.

## 2. requested family search 결과

이번 탐색은 `Quality Strict Annual`과 `Quality + Value Strict Annual`를 중심으로, 필요 시 `Value Strict Annual`도 함께 재검증했다.

### 결론

- `Quality Strict Annual`
  - `CAGR >= 15%`와 `MDD >= -20%`를 동시에 만족하는 non-hold 후보를 찾지 못함
- `Quality + Value Strict Annual`
  - `CAGR >= 15%`와 `MDD >= -20%`를 동시에 만족하는 non-hold 후보를 찾지 못함
- `Value Strict Annual`
  - 숫자 조건을 만족하는 exact-hit 후보는 찾았지만
  - `validation_caution` 때문에 여전히 `hold`

## 3. non-hold near-miss

요청한 조건에 가장 가까운 non-hold 후보들은 다음과 같다.

### Near miss 1

- family: `Quality + Value > Strict Annual`
- quality set: `q_balance_sheet`
  - `current_ratio, cash_ratio, debt_to_assets, debt_ratio`
- value set: `v_cashflow_only`
  - `ocf_yield, fcf_yield, pcr, pfcr`
- `month_end`
- `rebalance_interval = 6`
- `top_n = 30`
- benchmark: `LQD`
- result:
  - `promotion = production_candidate`
  - `shortlist = watchlist`
  - `deployment = review_required`
  - `CAGR = 5.89%`
  - `MDD = -19.76%`

### Near miss 2

- family: `Quality + Value > Strict Annual`
- quality set: `q_profitability`
  - `roe, roa, net_margin, operating_margin, gross_margin`
- value set: `v_asset_earnings`
  - `book_to_market, earnings_yield, operating_income_yield`
- `month_end`
- `rebalance_interval = 6`
- `top_n = 30`
- benchmark: `LQD`
- result:
  - `promotion = production_candidate`
  - `shortlist = watchlist`
  - `deployment = review_required`
  - `CAGR = 3.10%`
  - `MDD = -15.37%`

### Near miss 3

- family: `Quality + Value > Strict Annual`
- quality set: `q_capital_discipline`
  - `roe, roa, cash_ratio, debt_to_assets`
- value set: `v_asset_earnings`
  - `book_to_market, earnings_yield, operating_income_yield`
- `month_end`
- `rebalance_interval = 6`
- `top_n = 30`
- benchmark: `LQD`
- result:
  - `promotion = production_candidate`
  - `shortlist = watchlist`
  - `deployment = review_required`
  - `CAGR = 0.99%`
  - `MDD = -14.23%`

## 4. 해석

이번 탐색에서 확인된 핵심은 다음이다.

1. `hold`의 직접 원인은 수익률이나 drawdown 자체보다 `validation` 계층이었다.
2. `Quality`와 `Quality + Value`만으로는 requested constraint를 동시에 만족하는 non-hold exact hit를 만들지 못했다.
3. `Value`는 숫자 조건은 맞추지만, 현재 contract 기준에서는 여전히 `hold`다.
4. `Quality + Value`의 non-hold 후보들은 `hold`는 피했지만, CAGR이 크게 부족했다.

## 5. 운영 결론

현재 코드/계약 기준에서 사용자가 요청한 조건

- `hold 아님`
- `CAGR >= 15%`
- `MDD >= -20%`
- `start = 2016-01-01`
- `Historical Dynamic PIT Universe`
- `top_n <= 10`

을 동시에 만족하는 실전형 후보는 아직 찾지 못했다.

다음에 가장 실용적인 후속 조치는 다음 둘 중 하나다.

1. `validation_policy`를 더 세밀하게 풀 수 있는지 `Value` exact-hit 후보를 기준으로 좁혀 보기
2. `CAGR` 목표 또는 `MDD` 목표 중 하나를 완화하고, 그 안에서 `hold`가 아닌 후보를 다시 찾기
