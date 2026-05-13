# Phase 15 Value Downside Improvement Search First Pass

## 목적

Phase 15의 첫 작업은
`Value > Strict Annual` strongest baseline을 그대로 두고,
`Promotion = real_money_candidate`,
`Shortlist = paper_probation`,
`Deployment != blocked`
상태를 유지하면서
`MDD`를 더 낮출 수 있는 practical candidate가 있는지 찾는 것이다.

## 고정한 기준

- 전략:
  - `Value > Strict Annual`
- 기간:
  - `2016-01-01 ~ 2026-04-01`
- preset:
  - `US Statement Coverage 100`
- `Universe Contract`:
  - `Historical Dynamic PIT Universe`
- factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `Benchmark Contract`:
  - `Ticker Benchmark`
- `Benchmark Ticker`:
  - `SPY`
- practical `Real-Money Contract`:
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

## 이번 first pass에서 먼저 본 레버

- `Top N`
- `Rebalance Interval`
- `Trend Filter`
- `Market Regime`

핵심 질문은 이거였다.

- overlay나 cadence를 더 보수적으로 두면 `MDD`가 줄어드는가
- 그리고 그 상태에서도 `real_money_candidate / paper_probation`을 유지하는가

## representative rerun 결과

| Case | Top N | Rebalance Interval | Trend | Regime | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| strongest baseline | 10 | 1 | off | off | 29.89% | -29.15% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| refined candidate | 13 | 1 | off | off | 28.32% | -25.58% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| recommended downside-improved candidate | 14 | 1 | off | off | 27.48% | -24.55% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` |
| lower-MDD boundary case | 15 | 1 | off | off | 26.28% | -24.35% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` |

## 이번 first pass 결론

### 1. `Top N` 확대가 가장 깨끗한 downside lever였다

- strongest baseline `Top N = 10`은 여전히 raw return edge가 가장 강하다.
- 하지만 `Top N = 14`까지 넓히면
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
  를 그대로 유지하면서,
  `MDD`를 `-29.15% -> -24.55%`로 낮출 수 있었다.

즉:

- `CAGR`는 `29.89% -> 27.48%`로 내려가지만
- `MDD`는 `4.60%p` 개선된다.

### 2. `Top N = 15`는 숫자상 더 낮은 MDD지만 quality는 약간 떨어진다

- `Top N = 15`는 `MDD = -24.35%`로 더 낮다.
- 다만 `Rolling Review = caution`으로 내려간다.

즉:

- `Top N = 15`는 downside만 보면 더 좋지만
- practical candidate quality는 `Top N = 14`가 더 균형 잡혀 있다.

### 3. overlay / cadence는 이번 first pass에서 좋은 첫 레버가 아니었다

exploratory sweep 기준으로:

- `Trend Filter`
- `Market Regime`
- `Rebalance Interval > 1`

를 더 보수적으로 두면
일부 경우 `MDD`는 낮아졌지만,
`validation = caution`이 붙으면서 `hold`로 돌아가는 패턴이 반복됐다.

즉 이번 family에서는:

- gate를 유지한 채 downside를 줄이는 첫 레버는
  overlay보다 `Top N diversification` 쪽이었다.

## 이번 first pass 추천 후보

현재 Phase 15 first pass에서 가장 실무적으로 추천할 후보는:

- `Value > Strict Annual`
- same baseline factor set
- `Top N = 14`
- `Rebalance Interval = 1`
- `Trend Filter = off`
- `Market Regime = off`

이다.

이유:

- strongest baseline보다 drawdown이 확실히 낮고
- `Promotion / Shortlist / Deployment` 상태를 그대로 유지하며
- `Rolling Review`도 아직 `watch`를 유지하기 때문이다.

## 다음 단계

이번 first pass의 다음 자연스러운 작업은:

1. `Top N = 14` 후보를 downside-improved current candidate로 전략 로그에 고정
2. factor subset / controlled addition을 열어
   `Top N = 14`보다 더 낮은 `MDD` 또는 더 나은 consistency가 가능한지 확인
3. 이후 같은 방식으로
   `Quality`, `Quality + Value` family에도 candidate-improvement search를 시작

## 같이 보면 좋은 문서

- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md)
- [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
