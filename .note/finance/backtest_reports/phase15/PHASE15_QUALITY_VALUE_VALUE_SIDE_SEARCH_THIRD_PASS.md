# Phase 15 Quality Value Value-Side Search Third Pass

## 목적

`Quality + Value > Strict Annual`에서
`+ per` baseline은 이미

- `real_money_candidate`
- `small_capital_trial`
- `review_required`

까지 올라간 current strongest practical blended candidate다.

이번 third pass의 목적은 value side만 좁게 다시 보는 것이다.

- value factor를 1개 제거하면 더 나아지는가
- value factor를 1개 교체하면 더 나아지는가

## 고정 계약

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- quality anchor:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- value baseline:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `per`
- 구조:
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
- practical contract / guardrail:
  - current strict annual baseline 유지

## representative rerun 결과

| Case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| baseline | 29.43% | -27.43% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| remove `book_to_market` | 29.18% | -27.25% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| remove `earnings_yield` | 28.57% | -27.77% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| remove `sales_yield` | 28.50% | -30.84% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| replace `ocf_yield -> pcr` | 30.05% | -27.43% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |

보조 관찰:

- `remove_ocf_yield`
- `remove_operating_income_yield`
- `replace sales/ocf with fcf_yield`

계열은 canonical 범위에서 `hold / blocked`로 더 약하게 읽혔다.

## 해석

### 1. value-side removal은 baseline을 약하게 만든다

- `book_to_market` 제거
- `earnings_yield` 제거
- `sales_yield` 제거

는 모두

- `production_candidate / watchlist`

까지 gate tier가 내려간다.

즉:

- value side를 줄이는 것은
  이번 family에서 좋은 레버가 아니었다.

### 2. `ocf_yield -> pcr`는 baseline을 실제로 넘긴다

- baseline:
  - `CAGR = 29.43%`
  - `MDD = -27.43%`
  - `real_money_candidate / small_capital_trial / review_required`
- `ocf_yield -> pcr`:
  - `CAGR = 30.05%`
  - `MDD = -27.43%`
  - 같은 gate tier 유지

즉:

- gate를 유지하면서
- `CAGR`만 소폭 높인 current best replacement다.

## 현재 판단

- `Quality + Value + per` baseline은 strong했고,
  value-side를 줄이는 방향은 대체로 약해졌다.
- 하지만
  `ocf_yield -> pcr`
  replacement는 same risk / same gate tier에서
  `CAGR`만 개선하며 baseline을 넘겼다.

따라서 current strongest practical blended candidate는
이제

- `default quality`
- value:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `operating_income_yield`
  - `per`

로 읽는 편이 맞다.

## 다음 단계

자연스러운 다음 작업은:

1. `ocf_yield -> pcr` candidate를 전략 log와 hub에 current strongest practical point로 반영
2. 이 anchor에서
   - downside search
   - benchmark sensitivity
   - one-more replacement
   를 볼지 결정

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
