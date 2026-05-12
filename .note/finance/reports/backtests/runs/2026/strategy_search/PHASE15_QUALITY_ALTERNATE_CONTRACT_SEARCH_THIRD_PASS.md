# Phase 15 Quality Alternate Contract Search Third Pass

## 목적

`Quality > Strict Annual`은 Phase 15에서 structural rescue와 downside-improved candidate까지는 확보됐다.

이번 third pass의 질문은 더 실무적이다.

- 같은 rescued anchor를 유지한 채
- `benchmark / overlay` 계약을 조금 바꾸면

더 깨끗한 validation surface나 더 실전적인 deployment 해석이 나오는가

## 고정 anchor

- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- factor:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- baseline 구조:
  - `Option = month_end`
  - `Top N = 12`
  - `Rebalance Interval = 1`
  - `Benchmark = LQD`
  - `Trend Filter = on`
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

## 탐색 범위

- benchmark variation:
  - `LQD`
  - `SPY`
  - `QQQ`
  - `Candidate Universe Equal-Weight`
- overlay variation:
  - `Trend on / Regime off`
  - `Trend off / Regime off`
  - `Trend on / Regime on`

## representative rerun 결과

| Case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| baseline `LQD + trend on + regime off` | 26.02% | -25.57% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `normal` |
| balanced alternative `SPY + trend on + regime off` | 25.18% | -25.57% | `real_money_candidate` | `paper_probation` | `paper_only` | `normal` | `normal` | `normal` |
| prior rescued reference `LQD + trend on + regime on` | 14.84% | -27.97% | `production_candidate` | `watchlist` | `review_required` | `normal` | `normal` | `normal` |
| rejected defensive variant `LQD + trend off + regime off` | 17.30% | -35.84% | `hold` | `hold` | `blocked` | `caution` | `watch` | `caution` |
| rejected benchmark variant `QQQ + trend on + regime off` | 17%대 | -25%대 | `hold` | `hold` | `blocked` | `caution` | mixed | mixed |
| rejected benchmark variant `Candidate Universe Equal-Weight + trend on + regime off` | 20%대 | -20%대 후반 | `hold` | `hold` | `blocked` | `caution` | mixed | mixed |

## 해석

### 1. strongest practical point는 여전히 `LQD + trend on + regime off`

- `CAGR = 26.02%`
- `MDD = -25.57%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`

이번 pass에서는 이 baseline을 동시에 넘는 alternate contract가 없었다.

### 2. `SPY`는 cleaner alternative지만 deployment tier는 더 보수적이다

`SPY + trend on + regime off`는:

- `CAGR = 25.18%`
- `MDD = -25.57%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = paper_only`
- `Validation / Rolling / OOS = normal / normal / normal`

즉:

- surface는 baseline보다 더 깨끗하지만
- deployment 해석은 더 보수적으로 내려간다.

따라서 실무적으로는:

- strongest practical point는 `LQD`
- cleaner but more conservative alternative는 `SPY`

로 읽는 편이 맞다.

### 3. overlay를 더 방어적으로 바꾸는 것은 오히려 `hold`로 돌아가기 쉬웠다

특히 `Trend off / Regime off`는:

- `MDD`를 방어하지 못했고
- `validation = caution`
- `deployment = blocked`

로 후퇴했다.

즉 이번 anchor에서는:

- 추가 방어 overlay를 더한다고 좋아지는 게 아니라
- 현재 `trend on / regime off` 구조가 practical sweet spot에 가깝다.

## 현재 판단

- `Quality` family의 current recommended candidate는 변하지 않는다.
  - `LQD + trend on + regime off + Top N 12`
- 다만 operator 관점에서는
  - `SPY + trend on + regime off + Top N 12`
  도 같이 기억할 가치가 있다.
  - 이유:
    - `Validation / Rolling / OOS`가 모두 `normal`
    - 같은 `MDD`
    - 거의 비슷한 `CAGR`

즉:

- strongest practical candidate:
  - `LQD`
- cleaner alternative:
  - `SPY`

라는 두 점이 이번 third pass의 핵심 결론이다.

## 다음 단계

자연스러운 다음 작업은:

1. `Quality`는 현재 baseline을 유지
2. 당장 더 넓은 factor 변경보다
   `Quality + Value` new anchor follow-up에 리소스를 더 싣는다
3. `Quality`는 이후 필요할 때
   `benchmark semantics`
   또는
   `explicit weighting support`
   가 열리면 다시 확장 탐색한다

## 관련 문서

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md)
- [PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md)
