# Phase 17 Defensive Sleeve Risk-Off Representative Rerun First Pass

## 목적

이 문서는 Phase 17 두 번째 structural lever인
`defensive sleeve risk-off`를
current practical anchor에 적용했을 때
same-gate lower-MDD rescue가 가능한지 기록한다.

## 테스트한 contract

- `Risk-Off Mode = cash_only`
- `Risk-Off Mode = defensive_sleeve_preference`
- `Defensive Sleeve Tickers = BIL, SHY, LQD`

공통 전제:

- strict annual practical contract 유지
- `Market Regime = off`
- underperformance / drawdown guardrail `on`

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

| family | risk-off mode | CAGR | MDD | Promotion | Shortlist | Deployment |
|---|---|---:|---:|---|---|---|
| `Value` | `cash_only` | `28.21%` | `-24.55%` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Value` | `defensive_sleeve_preference` | `28.11%` | `-25.14%` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Quality + Value` | `cash_only` | `31.82%` | `-26.63%` | `real_money_candidate` | `small_capital_trial` | `review_required` |
| `Quality + Value` | `defensive_sleeve_preference` | `31.79%` | `-27.19%` | `real_money_candidate` | `small_capital_trial` | `review_required` |

## 관찰

- `defensive sleeve`는 두 family 모두 gate tier를 깨지 않았다.
- 하지만 이번 representative rerun에서는
  `MDD`를 낮추지 못했고 오히려 소폭 더 나빠졌다.
- activation도 많지 않았다.
  - `Value`:
    - `2` rows
    - `1.61%`
  - `Quality + Value`:
    - `3` rows
    - `2.42%`
- active reason은 전부 `drawdown_guardrail`이었다.

## activation row

### Value

- `2022-04-29`
- `2022-05-31`

### Quality + Value

- `2018-11-30`
- `2022-04-29`
- `2022-05-31`

## 구현 메모

first slice wiring 이후 representative rerun에서
defensive sleeve ETF가 strict annual candidate pool로 잘못 섞여
`Liquidity Excluded Count`를 오염시키는 회귀가 있었다.

이번 pass에서 이를 같이 수정했다.

- candidate universe와 defensive sleeve ticker를 분리
- defensive sleeve active count/share를 strict annual meta에도 남김

즉 이번 결과는 회귀 수정 후 기준 숫자다.

## 해석

- `partial cash retention`은 downside는 크게 줄였지만 cash drag가 컸다.
- `defensive sleeve risk-off`는 cash drag는 줄였지만
  current anchor에서는 downside 개선으로 이어지지 않았다.

따라서 현재 결론은:

- `Value` current anchor 유지
- `Quality + Value` current strongest practical point 유지
- next structural lever는
  `concentration-aware weighting`
  쪽이 더 자연스럽다

## 관련 문서

- [PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/runs/2026/strategy_search/PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md)
- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
