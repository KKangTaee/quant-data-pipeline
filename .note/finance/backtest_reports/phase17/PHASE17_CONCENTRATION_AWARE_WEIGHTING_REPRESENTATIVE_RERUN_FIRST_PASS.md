# Phase 17 Concentration-Aware Weighting Representative Rerun First Pass

## 목적

이 문서는 Phase 17 세 번째 structural lever인
`concentration-aware weighting`을
current practical anchor에 적용했을 때
same-gate lower-MDD rescue가 가능한지 기록한다.

## 테스트한 contract

- `Weighting Mode = equal_weight`
- `Weighting Mode = rank_tapered`

공통 전제:

- strict annual practical contract 유지
- `Market Regime = off`
- underperformance / drawdown guardrail `on`
- `partial cash retention = off`
- `risk_off_mode = cash_only`

## 대표 후보

### 1. Value

- anchor:
  - `Top N = 14`
  - factors:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `psr`
  - `Benchmark = SPY`

### 2. Quality + Value

- anchor:
  - quality:
    - `roe`
    - `roa`
    - `operating_margin`
    - `asset_turnover`
    - `current_ratio`
  - value:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `pcr`
    - `por`
    - `per`
  - `Top N = 10`
  - `Benchmark Contract = Candidate Universe Equal-Weight`

## 결과 요약

| family | weighting mode | CAGR | MDD | Promotion | Shortlist | Deployment |
|---|---|---:|---:|---|---|---|
| `Value` | `equal_weight` | `28.13%` | `-24.55%` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Value` | `rank_tapered` | `27.71%` | `-25.87%` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Quality + Value` | `equal_weight` | `31.82%` | `-26.63%` | `real_money_candidate` | `small_capital_trial` | `review_required` |
| `Quality + Value` | `rank_tapered` | `32.92%` | `-27.60%` | `real_money_candidate` | `small_capital_trial` | `review_required` |

## 관찰

- `rank_tapered`는 두 family 모두 gate tier를 깨지 않았다.
- 하지만 이번 representative rerun에서는
  `MDD`를 낮추지 못했다.
  - `Value`:
    - `-24.55% -> -25.87%`
  - `Quality + Value`:
    - `-26.63% -> -27.60%`
- `Quality + Value`에서는 `CAGR`가 오히려 올라갔지만,
  downside 개선이라는 현재 질문에는 맞지 않았다.
- `Value`에서는 `Rolling Review`도
  `watch -> caution`으로 한 단계 더 약해졌다.

## 해석

- `partial cash retention`은 downside는 크게 줄였지만 cash drag가 컸다.
- `defensive sleeve risk-off`는 gate는 유지했지만 `MDD`를 더 낮추지 못했다.
- `concentration-aware weighting`은
  gate를 유지한 채 `equal-weight` 대안으로 잘 동작했지만,
  current anchor에서는 역시 lower-MDD rescue를 만들지 못했다.

따라서 현재 결론은:

- `Value` current anchor 유지
- `Quality + Value` current strongest practical point 유지
- Phase 17 first three structural levers 기준으로는
  same-gate lower-MDD exact rescue가 아직 없다

## 관련 문서

- [PHASE17_CONCENTRATION_AWARE_WEIGHTING_IMPLEMENTATION_THIRD_SLICE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_IMPLEMENTATION_THIRD_SLICE.md)
- [PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md)
- [PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md)
- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
