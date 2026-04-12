# Phase 15 Value Factor Addition Second Pass

## 목적

Phase 15 첫 downside-improvement 결과에서
`Top N = 14`가 strongest baseline보다 더 균형 잡힌 후보라는 점을 확인한 뒤,
이번 second pass에서는 **factor addition만** 바꾸어
`MDD`를 더 낮추거나 최소한 유지하면서 `CAGR`를 지킬 수 있는지 확인한다.

## 고정한 기준

- 전략:
  - `Value > Strict Annual`
- baseline anchor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `Top N`:
  - `14`
- `Rebalance Interval`:
  - `1`
- 기간:
  - `2016-01-01 ~ 2026-04-01`
- preset:
  - `US Statement Coverage 100`
- `Universe Contract`:
  - `Historical Dynamic PIT Universe`
- `Benchmark`:
  - `SPY`
- practical `Real-Money Contract`:
  - strongest candidate 기준
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

## 추가한 factor 후보

- `fcf_yield`
- `liquidation_value`
- `pcr`
- `pfcr`
- `ev_ebit`
- `por`
- `per`
- `pbr`
- `psr`

## 전체 결과 요약

| Added Factor | Promotion | Shortlist | Deployment | Validation | Rolling | OOS | CAGR | MDD |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: |
| `fcf_yield` | `production_candidate` | `watchlist` | `review_required` | `watch` | `caution` | `caution` | 23.16% | -28.21% |
| `liquidation_value` | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` | 29.36% | -26.82% |
| `pcr` | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` | 24.58% | -31.86% |
| `pfcr` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` | 23.73% | -28.21% |
| `ev_ebit` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `caution` | 22.73% | -27.33% |
| `por` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` | 26.88% | -25.06% |
| `per` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` | 27.49% | -25.55% |
| `pbr` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `caution` | `caution` | 25.83% | -25.67% |
| `psr` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `caution` | 28.13% | -24.55% |

## non-hold 정렬

MDD가 낮은 순으로 보면:

1. `psr`
   - `Promotion = real_money_candidate`
   - `Shortlist = paper_probation`
   - `Deployment = review_required`
   - `CAGR = 28.13%`
   - `MDD = -24.55%`
2. `ev_ebit`
   - `Promotion = real_money_candidate`
   - `Shortlist = paper_probation`
   - `Deployment = review_required`
   - `CAGR = 22.73%`
   - `MDD = -27.33%`
3. `por`
   - `Promotion = real_money_candidate`
   - `Shortlist = paper_probation`
   - `Deployment = review_required`
   - `CAGR = 26.88%`
   - `MDD = -25.06%`
4. `per`
   - `Promotion = real_money_candidate`
   - `Shortlist = paper_probation`
   - `Deployment = review_required`
   - `CAGR = 27.49%`
   - `MDD = -25.55%`
5. `pbr`
   - `Promotion = real_money_candidate`
   - `Shortlist = paper_probation`
   - `Deployment = review_required`
   - `CAGR = 25.83%`
   - `MDD = -25.67%`
6. `pfcr`
   - `Promotion = real_money_candidate`
   - `Shortlist = paper_probation`
   - `Deployment = review_required`
   - `CAGR = 23.73%`
   - `MDD = -28.21%`
7. `fcf_yield`
   - `Promotion = production_candidate`
   - `Shortlist = watchlist`
   - `Deployment = review_required`
   - `CAGR = 23.16%`
   - `MDD = -28.21%`

## 이번 second pass 결론

### 1. `psr` addition이 가장 좋은 second-pass candidate다

- `psr`를 추가한 경우:
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
  - `Validation = normal`
  - `Rolling Review = watch`
  - `Out-of-Sample Review = caution`
- 그리고 숫자는:
  - `CAGR = 28.13%`
  - `MDD = -24.55%`

이는 Phase 15 first-pass downside-improved candidate인 `Top N = 14` baseline과 사실상 같은 MDD를 유지하면서,
`CAGR`은 더 높다.

### 2. `ev_ebit` / `por` / `per` / `pbr`는 후보군을 바꿀 수는 있지만 더 좋지는 않았다

- `ev_ebit`는 안정적이지만 CAGR이 너무 내려간다.
- `por`와 `per`는 baseline보다 낫지만 `psr`보다 균형이 약하다.
- `pbr`는 `MDD` 측면에서 `psr`보다 약간 뒤진다.

### 3. `fcf_yield`는 non-hold이지만 watchlist로 내려간다

- `fcf_yield` 추가는 전략을 살짝 더 방어적으로 만들지만
  `Promotion = production_candidate`
  `Shortlist = watchlist`
  까지 내려간다.
- 즉 first-pass보다 더 좋은 practical candidate는 아니었다.

## 이번 second pass 추천 후보

현재 Phase 15 second pass에서 가장 추천할 후보는:

- `Value > Strict Annual`
- base factors:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `Top N = 14`
- `Rebalance Interval = 1`
- plus one additional factor:
  - `psr`

## 해석

- first-pass candidate `Top N = 14`는 strong balanced anchor였다.
- second pass에서는 `psr`를 더한 버전이
  같은 `MDD` 수준을 유지하면서 `CAGR`를 조금 더 끌어올렸다.
- 따라서 현재까지의 best practical `Value` candidate는
  **`baseline 5-factor + psr + Top N 14`** 로 읽는 것이 가장 자연스럽다.

## 다음 단계

이번 second pass의 다음 자연스러운 작업은:

1. `psr` addition candidate를 strategy log와 hub snapshot에 고정
2. `Quality` / `Quality + Value` family에서도 같은 controlled addition search를 수행
3. 필요하면 `Top N 14`를 유지한 채 `Top N 13/15`와의 tradeoff를 다시 한 번 좁혀 본다

## 같이 보면 좋은 문서

- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
- [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
