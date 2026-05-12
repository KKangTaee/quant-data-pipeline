# Phase 15 Quality Value Replacement-Anchor Follow-Up Fourth Pass

## 목적

`Quality + Value > Strict Annual`의 current strongest practical point는
value-side third pass에서 나온
`ocf_yield -> pcr` replacement anchor다.

이번 fourth pass의 질문은 간단하다.

- 이 new anchor에서 `Top N`을 다시 흔들면 더 좋아지는가
- benchmark를 바꾸면 same candidate가 더 실무적으로 읽히는가

## 고정 anchor

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
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
  - `pcr`
  - `operating_income_yield`
  - `per`
- 구조:
  - `Option = month_end`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
- practical contract:
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - `Min Benchmark Coverage = 95%`
  - `Min Net CAGR Spread = -2%`
  - `Min Liquidity Clean Coverage = 90%`
  - `Max Underperformance Share = 55%`
  - `Min Worst Rolling Excess = -15%`
  - `Max Strategy Drawdown = -35%`
  - `Max Drawdown Gap vs Benchmark = 8%`
- guardrail:
  - underperformance `on / 12M / -10%`
  - drawdown `on / 12M / -35% / 8%`

주의:

- UI는 `%` 입력을 내부 runtime ratio로 바꿔서 넘긴다.
- direct runtime 검증에서는 위 threshold를
  - `0.95`
  - `-0.02`
  - `0.90`
  - `0.55`
  - `-0.15`
  - `-0.35`
  - `0.08`
  처럼 ratio로 넣어야 같은 결과가 난다.

## 탐색 범위

- `Top N`:
  - `8`
  - `10`
  - `12`
  - `14`
  - `16`
- benchmark:
  - `Candidate Universe Equal-Weight`
  - `Ticker Benchmark = SPY`

## representative rerun 결과

| Case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| baseline `Top N 10 + Candidate Universe Equal-Weight` | 30.05% | -27.43% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `Top N 8 + Candidate Universe Equal-Weight` | 31.69% | -27.64% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `Top N 12 + Candidate Universe Equal-Weight` | 27.06% | -28.28% | `hold` | `hold` | `blocked` | `caution` | `watch` | `normal` |
| `Top N 14 + Candidate Universe Equal-Weight` | 25.98% | -28.61% | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| `Top N 16 + Candidate Universe Equal-Weight` | 25.32% | -27.46% | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| `Top N 10 + Ticker Benchmark = SPY` | 30.05% | -27.43% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |

## 해석

### 1. `Top N = 10 + Candidate Universe Equal-Weight`가 여전히 strongest practical point다

- `CAGR = 30.05%`
- `MDD = -27.43%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`

이번 fourth pass에서도 이 baseline을 넘는 `Top N` 대안은 없었다.

### 2. `Top N = 8`은 수익률은 더 높지만 gate tier를 잃는다

- `CAGR = 31.69%`
- `MDD = -27.64%`
- `Promotion = production_candidate`
- `Shortlist = watchlist`

즉:

- raw return은 더 공격적이지만
- 실전 후보 tier는 오히려 내려간다.

### 3. `Top N >= 12`는 다시 `hold / blocked`로 후퇴한다

`12`, `14`, `16`은 모두

- `Validation = caution`
또는
- `Rolling = caution`

축이 약해지며
`hold / blocked`로 내려간다.

### 4. benchmark를 `SPY`로 바꾸면 shortlist tier만 한 단계 내려간다

`Top N = 10 + Ticker Benchmark = SPY`는

- same `CAGR`
- same `MDD`
- same `Promotion = real_money_candidate`

지만,

- `Shortlist = paper_probation`

으로 내려간다.

## 현재 판단

- `ocf_yield -> pcr` replacement anchor는 유효하다.
- 하지만 그 anchor 위에서
  - `Top N`
  - benchmark
를 다시 흔들어도
현재 strongest practical point를 넘지는 못했다.

즉 현재 `Quality + Value`의 recommended candidate는 그대로:

- `Top N = 10`
- `Candidate Universe Equal-Weight`
- value replacement:
  - `ocf_yield -> pcr`

이다.

## 다음 단계

자연스러운 다음 작업은:

1. `Quality + Value` current strongest practical point를 그대로 유지
2. 필요하면 다음에는
   - one-more bounded replacement
   - value-side bounded addition
   - benchmark semantics cleanup
   중 하나만 좁게 시도
3. 아니면 Phase 15를 current strongest candidates 정리 중심으로 closeout 준비

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
- [PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase15/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md)
- [PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase15/PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md)
