# Phase 15 Quality Value PER Benchmark And Pruning Search Second Pass

## 목적

`Quality + Value > Strict Annual`에서
`+ per` addition anchor는 이미

- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`

까지 올라간 current strongest practical blended candidate다.

이번 pass의 질문은 두 가지다.

- benchmark를 바꾸면 gate나 risk/return이 더 좋아지는가
- quality-side pruning만으로 더 깨끗한 blended candidate가 나오는가

## 고정 계약

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- factor anchor:
  - quality:
    - `roe`
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - value:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `per`
- core settings:
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`

## 이번 second pass에서 본 레버

- benchmark sensitivity:
  - `Candidate Universe Equal-Weight`
  - `Ticker Benchmark = SPY`
  - `Ticker Benchmark = LQD`
- quality-side pruning:
  - `current_ratio` 제거
  - `asset_turnover` 제거
  - `net_margin` 제거

## representative rerun 결과

| Case | Benchmark | Quality Factors | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| current strongest practical baseline | `Candidate Universe Equal-Weight` | full anchor | 29.43% | -27.43% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| ticker benchmark alternative | `Ticker Benchmark = SPY` | full anchor | 29.43% | -27.43% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |
| defensive benchmark failure | `Ticker Benchmark = LQD` | full anchor | 19.77% | -35.37% | `hold` | `hold` | `blocked` | `caution` | `watch` | `watch` |
| prune `current_ratio` | `Candidate Universe Equal-Weight` | `roe, roa, net_margin, asset_turnover` | 27.44% | -26.93% | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| prune `asset_turnover` | `Candidate Universe Equal-Weight` | `roe, roa, net_margin, current_ratio` | 27.39% | -28.61% | `hold` | `hold` | `blocked` | `caution` | `watch` | `normal` |
| prune `net_margin` | `Candidate Universe Equal-Weight` | `roe, roa, asset_turnover, current_ratio` | 28.13% | -27.61% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |

## 해석

### 1. current baseline이 여전히 strongest practical point다

- `Candidate Universe Equal-Weight + per` baseline은
  - `real_money_candidate`
  - `small_capital_trial`
  - `review_required`
  를 그대로 유지한다.
- 이번 second pass에서
  이 shortlist tier를 유지한 대안은 없었다.

### 2. `Ticker Benchmark = SPY`는 숫자는 같아도 shortlist tier가 낮아진다

- `CAGR`와 `MDD`는 baseline과 사실상 같다.
- 하지만 `Shortlist`가
  - `small_capital_trial -> paper_probation`
  으로 내려간다.

즉:

- same strategy performance라도
- current practical contract에서는
  `Candidate Universe Equal-Weight` 해석이 더 강한 shortlist tier를 만든다.

### 3. quality-side pruning은 baseline을 넘지 못했다

- `current_ratio` 제거:
  - `MDD`는 조금 좋아졌지만 `validation = caution`으로 `hold`
- `asset_turnover` 제거:
  - `CAGR`와 `MDD` 모두 baseline보다 약해지고 `hold`
- `net_margin` 제거:
  - `CAGR`는 상대적으로 유지됐지만 역시 `hold`

즉 이번 second pass에서는:

- simple quality pruning이 blended candidate quality를 개선하는 주된 레버가 아니었다.

## 현재 판단

- `Quality + Value + per`는
  current practical contract 기준으로도
  여전히 `Candidate Universe Equal-Weight` benchmark 아래의 baseline이 strongest practical point다.
- 즉 다음 레버는
  - benchmark 변경
  - 단순 quality pruning
  보다
  - value-side replacement
  - 더 bounded한 downside search
  - factor weighting / structural blend 조정
  쪽에 더 가깝다.

## 다음 단계

자연스러운 다음 작업은:

1. current baseline을 계속 anchor로 유지
2. `quality pruning` 대신
   `value-side replacement / bounded removal`
   쪽으로 넘어가 보기
3. 또는 family별 strongest candidate roster를 한 장으로 다시 정리

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase15/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md)
