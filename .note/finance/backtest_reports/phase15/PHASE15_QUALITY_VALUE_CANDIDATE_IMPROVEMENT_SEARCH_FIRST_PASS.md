# Phase 15 Quality Value Candidate Improvement Search First Pass

## 목적

`Quality + Value > Strict Annual` family의 strongest non-hold blend anchor에
bounded single-factor addition을 붙였을 때,

- `Promotion`
- `Shortlist`
- `Deployment`

를 더 올릴 수 있는지 확인한다.

## 고정 계약

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- anchor factor:
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

## 탐색 범위

- anchor rerun
- one-factor additions only:
  - `interest_coverage`
  - `ocf_margin`
  - `fcf_margin`
  - `net_debt_to_equity`
  - `dividend_payout`
  - `gpa`
  - `per`
  - `pcr`
  - `por`
  - `liquidation_value`

## 결과 요약

| Case | Added Factor | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| baseline | `-` | `28.51%` | `-28.35%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `+ interest_coverage` | quality | `21.72%` | `-28.74%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `+ ocf_margin` | quality | `27.66%` | `-30.37%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `+ fcf_margin` | quality | `17.89%` | `-34.17%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` |
| `+ net_debt_to_equity` | quality | `23.39%` | `-31.45%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `caution` |
| `+ dividend_payout` | quality | `21.55%` | `-31.39%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `caution` |
| `+ gpa` | quality | `29.38%` | `-28.46%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `+ per` | value | `29.43%` | `-27.43%` | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `+ pcr` | value | `29.74%` | `-26.50%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `+ por` | value | `29.35%` | `-26.99%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `+ liquidation_value` | value | `33.16%` | `-26.06%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |

## 해석

- 가장 좋은 practical addition 결과는 `per`였다.
  - `CAGR 28.51% -> 29.43%`
  - `MDD -28.35% -> -27.43%`
  - gate도 함께 올라갔다
    - `production_candidate -> real_money_candidate`
    - `watchlist -> small_capital_trial`
    - `deployment = review_required` 유지
- 따라서 `per`는 이번 pass의 current best addition candidate이자
  current strongest practical blended candidate로 볼 수 있다.
- `pcr`, `por`는 drawdown은 더 좋아졌지만
  `production_candidate / watchlist`에 머물러
  gate progression 측면에서는 `per`보다 약했다.
- `liquidation_value`는 숫자 자체는 가장 공격적이었지만,
  validation이 `caution`으로 떨어져 `hold / blocked`가 되었다.
- quality expansion factor 대부분은 blended family에서도
  validation을 악화시키는 쪽으로 작동했다.

## 현재 판단

- `Quality + Value` family는 bounded one-factor addition만으로도
  current code 기준 stronger practical candidate를 만들 수 있었다.
- 그 결과는 `per` addition이며,
  이번 pass에서는 baseline을 실제로 대체하는 current best candidate다.
- 다음 액션은
  - `per` candidate 기준 downside-improvement search
  - `top-N sensitivity`
  - `quality factor replacement`
  같은 구조적 실험 쪽이 더 자연스럽다.

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase14/PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md)
