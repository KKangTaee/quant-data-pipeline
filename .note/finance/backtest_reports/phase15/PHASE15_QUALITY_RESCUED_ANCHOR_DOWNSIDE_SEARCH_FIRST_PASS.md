# Phase 15 Quality Rescued Anchor Downside Search First Pass

## 목적

`Quality > Strict Annual` family는 structural rescue second pass에서

- `capital_discipline`
- `Benchmark = LQD`
- `Trend Filter = on`
- `Market Regime = off`
- `Top N = 10`

조합으로
`real_money_candidate / paper_probation / review_required`
를 회복했다.

이번 pass의 목적은 이 rescued anchor를 그대로 두고,

- `Top N`
- `Rebalance Interval`

만 조정해도 더 나은 downside / consistency tradeoff가 나오는지 확인하는 것이다.

## 고정 계약

- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- factor anchor:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- benchmark / overlay:
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
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

## 탐색 범위

- `Top N`:
  - `6`
  - `8`
  - `10`
  - `12`
  - `14`
  - `16`
- `Rebalance Interval`:
  - `1`
  - `2`
  - `3`

## representative rerun 결과

| Case | Top N | Rebalance Interval | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| lower-conviction | 6 | 1 | 18.84% | -31.63% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| higher-upside near-miss | 8 | 1 | 25.11% | -30.07% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `caution` |
| rescued anchor baseline | 10 | 1 | 24.28% | -31.48% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |
| recommended downside-improved candidate | 12 | 1 | 26.02% | -25.57% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `normal` |
| broader diversification | 14 | 1 | 21.89% | -25.95% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `normal` |
| conservative clean candidate | 16 | 1 | 20.23% | -25.73% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |

보조 관찰:

- `Rebalance Interval = 2 / 3`는 이번 범위에서는 전부 `hold / blocked`였다.
- 즉 rescued anchor에서는 cadence보다 `Top N diversification`이 더 유효한 downside lever였다.

## 해석

### 1. `Top N = 12`가 이번 pass의 recommended downside-improved candidate다

- baseline `Top N = 10` 대비:
  - `CAGR`:
    - `24.28% -> 26.02%`
  - `MDD`:
    - `-31.48% -> -25.57%`
- gate:
  - `real_money_candidate`
  - `paper_probation`
  - `review_required`
  를 그대로 유지한다.

즉:

- 수익률도 오르고
- 낙폭도 `5.91%p` 개선되지만
- `Rolling Review = watch`로 한 단계 내려간다.

### 2. `Top N = 16`은 more conservative but cleaner choice다

- `CAGR = 20.23%`
- `MDD = -25.73%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation / Rolling / OOS = normal / normal / normal`

즉:

- absolute return은 `Top N = 12`보다 낮지만
- consistency surface는 더 깨끗하다.

### 3. `Top N = 8`은 upside는 강하지만 OOS가 약하다

- `CAGR = 25.11%`
- `MDD = -30.07%`
- gate는 유지되지만
- `OOS = caution`이 붙는다.

따라서 strongest practical next anchor로 삼기에는
`Top N = 12`나 `16`보다 우선순위가 낮다.

## 현재 판단

- `Quality` rescued anchor는 `hold`를 벗어나는 데서 끝나지 않고,
  `Top N` 조정만으로도 상당한 downside improvement가 가능하다.
- 이번 pass의 운영 추천은 두 가지다.
  - practical recommended candidate:
    - `Top N = 12`
  - conservative clean candidate:
    - `Top N = 16`

## 다음 단계

다음으로 자연스러운 작업은:

1. `Top N = 12`를 `Quality` downside-improved current candidate로 전략 로그에 고정
2. 같은 rescued contract 위에서
   `bounded factor addition / replacement`
   를 다시 붙여도 `real_money_candidate`를 유지하는지 확인
3. 필요하면 `Top N = 16`을 conservative alternative로 같이 유지

## 관련 문서

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md)
