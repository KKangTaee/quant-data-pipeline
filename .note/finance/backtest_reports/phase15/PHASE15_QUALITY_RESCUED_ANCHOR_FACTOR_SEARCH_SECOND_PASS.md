# Phase 15 Quality Rescued Anchor Factor Search Second Pass

## 목적

`Quality > Strict Annual` rescued anchor downside search first pass에서
`Top N = 12`가 recommended downside-improved current candidate로 올라왔다.

이번 second pass의 질문은 단순하다.

- 이 rescued contract 위에 factor를 하나 더 붙이거나
- 기존 factor 하나를 바꾸면

더 좋은 practical candidate가 나오는가

## 고정 계약

- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- rescued anchor:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- 구조:
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
  - `Top N = 12`
  - `Rebalance Interval = 1`
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

### bounded addition

- `net_debt_to_equity`
- `interest_coverage`
- `ocf_margin`
- `fcf_margin`
- `operating_margin`
- `gross_margin`
- `debt_ratio`

### bounded replacement

- `debt_to_assets -> net_debt_to_equity`
- `cash_ratio -> interest_coverage`
- `roa -> ocf_margin`
- `roa -> fcf_margin`
- `debt_to_assets -> debt_ratio`

## representative rerun 결과

| Case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| rescued-anchor baseline | 26.02% | -25.57% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `watch` | `normal` |
| `+ net_debt_to_equity` | 20.25% | -30.32% | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `caution` |
| `+ interest_coverage` | 20.10% | -34.89% | `hold` | `hold` | `blocked` | `caution` | `normal` | `watch` |
| `+ gross_margin` | 16.32% | -30.00% | `hold` | `hold` | `blocked` | `caution` | `normal` | `caution` |
| `debt_to_assets -> net_debt_to_equity` | 16.86% | -29.49% | `hold` | `hold` | `blocked` | `caution` | `watch` | `normal` |

## 해석

### 1. 이번 second pass에서는 baseline을 넘는 bounded factor 변화가 없었다

- rescued-anchor baseline:
  - `CAGR = 26.02%`
  - `MDD = -25.57%`
  - `real_money_candidate / paper_probation / review_required`
- 어떤 addition / replacement도
  같은 gate를 유지하면서
  baseline보다 더 좋은 `CAGR / MDD` 조합을 만들지 못했다.

### 2. `+ net_debt_to_equity`만 non-hold를 유지했지만 practical quality는 후퇴했다

- 장점:
  - `Promotion / Shortlist / Deployment`는 유지
  - `Rolling = normal`
- 단점:
  - `CAGR = 20.25%`
  - `MDD = -30.32%`
  - `OOS = caution`

즉:

- consistency 한 축은 좋아졌지만
- 수익률과 낙폭이 함께 나빠져
  recommended candidate로 올리기 어렵다.

### 3. 다른 addition / replacement는 대체로 validation이 깨지며 `hold`로 돌아갔다

- `interest_coverage`
- `ocf_margin`
- `fcf_margin`
- `operating_margin`
- `gross_margin`
- `debt_ratio`

계열은 이번 rescued contract 위에서도
대부분 `validation = caution`을 만들며 `hold / blocked`로 후퇴했다.

## 현재 판단

- `Quality`의 current best practical point는 여전히
  rescued-anchor downside-improved baseline:
  - `Top N = 12`
  - `roe, roa, cash_ratio, debt_to_assets`
  이다.
- 이번 second pass는
  factor를 더 붙이는 것보다
  현재 구조를 유지하는 편이 더 낫다는 결론을 남긴다.

## 다음 단계

자연스러운 다음 작업은:

1. `Quality` current best practical point를 그대로 유지
2. factor 추가보다
   - weighting
   - rebalance semantics
   - alternate overlay contract
   같은 구조 실험으로 넘어가기

## 관련 문서

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md)
