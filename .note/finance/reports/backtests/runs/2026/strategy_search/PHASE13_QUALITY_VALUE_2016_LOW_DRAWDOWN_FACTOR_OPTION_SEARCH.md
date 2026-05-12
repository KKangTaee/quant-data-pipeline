# PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH

## 목적

사용자가 다음 고정 조건을 준 상태에서 `Quality + Value` family 안에서 추가 탐색을 진행했다.

- 전략 family: `Quality + Value`
- variant: `Strict Annual`
- `Universe Contract = Historical Dynamic PIT Universe`
- 시작일: `2016-01-01`
- 목표:
  - `hold`가 아닌 상태
  - `Maximum Drawdown >= -15%`

이번 문서는 **factor 조합 자체를 바꾸고**, 그 위에 **리밸런싱 cadence / benchmark**를 다시 조정했을 때 결과가 어떻게 달라지는지 기록한다.

## 공통 실행 계약

- preset: `US Statement Coverage 100`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- `Trend Filter = on`
- `Market Regime = on`
- `Underperformance Guardrail = on`
- `Drawdown Guardrail = on`

## 1. 방어적 factor 조합 탐색

먼저 drawdown을 낮추기 쉬운 방향으로 quality / value factor를 다시 묶었다.

### Quality 후보

- `q_balance_sheet`
  - `current_ratio`, `cash_ratio`, `debt_to_assets`, `debt_ratio`
- `q_capital_discipline`
  - `roe`, `roa`, `cash_ratio`, `debt_to_assets`
- `q_profitability`
  - `roe`, `roa`, `net_margin`, `operating_margin`, `gross_margin`

### Value 후보

- `v_cashflow_only`
  - `ocf_yield`, `fcf_yield`, `pcr`, `pfcr`
- `v_asset_earnings`
  - `book_to_market`, `earnings_yield`, `operating_income_yield`

### 먼저 본 리밸런싱 설정

- `month_end`, `rebalance_interval = 6`, `top_n = 30`
- `year_end`, `rebalance_interval = 12`, `top_n = 30`

## 2. drawdown 기준만 보면 가장 나았던 조합

`Candidate Universe Equal-Weight` benchmark 기준으로는 아래 조합이 가장 낮은 drawdown을 만들었다.

### Best low-drawdown case

- quality set: `q_balance_sheet`
- value set: `v_cashflow_only`
- `option = month_end`
- `rebalance_interval = 6`
- `top_n = 30`
- 결과:
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`
  - `validation = caution`
  - `rolling = caution`
  - `out_of_sample = caution`
  - `CAGR = 2.40%`
  - `MDD = -13.57%`

### 비슷한 근접 조합

- `q_balance_sheet + v_asset_earnings`
  - `month_end / 6 / top_n 30`
  - `CAGR = 1.04%`
  - `MDD = -13.67%`
  - 상태: `hold`
- `q_capital_discipline + v_asset_earnings`
  - `month_end / 6 / top_n 30`
  - `CAGR = 0.99%`
  - `MDD = -14.23%`
  - 상태: `hold`

즉 **factor 조합을 바꾸면 MDD를 15% 이내까지 낮추는 것은 가능**했지만, 이 경우에는 `validation_caution`이 남아서 `hold`를 벗어나지 못했다.

## 3. benchmark를 바꿔 hold를 벗어나는지 확인

위의 상위 조합에 대해 `TLT`, `IEF`, `LQD` benchmark를 다시 붙여서 `hold`가 풀리는지 확인했다.

### 결과 요약

- `TLT`
  - 여전히 대부분 `hold`
  - `MDD`는 대체로 `-19% ~ -22%`
- `IEF`
  - 여전히 대부분 `hold`
  - `MDD`는 대체로 `-20% ~ -25%`
- `LQD`
  - 일부 조합이 `production_candidate`까지 올라감
  - 하지만 `MDD`는 다시 `-19% ~ -22%` 수준으로 커짐

### Best non-hold defensive case

- quality set: `q_balance_sheet`
- value set: `v_cashflow_only`
- `option = month_end`
- `rebalance_interval = 6`
- `top_n = 30`
- `benchmark = LQD`
- 결과:
  - `promotion = production_candidate`
  - `shortlist = watchlist`
  - `deployment = review_required`
  - `validation = watch`
  - `benchmark_policy = normal`
  - `validation_policy = normal`
  - `guardrail_policy = normal`
  - `rolling = watch`
  - `out_of_sample = normal`
  - `CAGR = 5.89%`
  - `MDD = -19.76%`

## 4. Best non-hold case를 더 미세조정한 결과

가장 유망했던 `q_balance_sheet + v_cashflow_only + LQD` 조합에서 `top_n`과 interval을 더 바꿔 봤다.

### 확인한 설정

- `month_end`, interval `3`, top `20`
- `month_end`, interval `3`, top `30`
- `month_end`, interval `6`, top `20`
- `month_end`, interval `6`, top `30`
- `month_end`, interval `6`, top `40`
- `month_end`, interval `6`, top `50`
- `year_end`, interval `12`, top `30`
- `year_end`, interval `12`, top `50`

### 가장 나은 non-hold 결과

- `month_end`
- `rebalance_interval = 6`
- `top_n = 40` 또는 `50`
- 결과:
  - `promotion = production_candidate`
  - `shortlist = watchlist`
  - `deployment = review_required`
  - `validation = watch`
  - `CAGR ≈ 5.48%`
  - `MDD ≈ -18.91%`

즉 non-hold를 유지한 상태에서 drawdown을 조금 더 낮출 수는 있었지만, **여전히 `-15%` 안으로는 못 들어왔다.**

## 결론

이번 추가 탐색으로 확인된 것은 다음과 같다.

1. `factor`를 방어적으로 바꾸면 `Quality + Value`의 drawdown은 실제로 내려간다.
2. 하지만 그 상태에서는 `validation_caution`이 남아 `hold`가 유지되는 경우가 많다.
3. `benchmark`를 `LQD`처럼 더 방어적인 쪽으로 바꾸면 일부 조합이 `production_candidate`까지 올라간다.
4. 다만 그 순간 drawdown이 다시 커져서, **`hold 아님` + `MDD 15% 이내`를 동시에 만족하는 조합은 이번 탐색 범위 안에서 찾지 못했다.**

## 운영 해석

현재 코드/데이터/계약 기준에서 `Quality + Value > Strict Annual`에 대해:

- `2016-01-01` 시작
- `Historical Dynamic PIT Universe`
- `hold 아님`
- `Maximum Drawdown >= -15%`

을 동시에 요구하는 것은 여전히 매우 빡빡하다.

실무적으로 다음 선택지가 더 현실적이다.

1. `MDD` 목표를 `20%` 전후로 완화
2. 시작일을 더 짧게 잡기
3. `Quality + Value`는 `watchlist / paper probation`용으로 보고, 더 강한 저낙폭 목표는 다른 family에서 찾기
