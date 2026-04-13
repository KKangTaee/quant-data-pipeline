# Quality Value Strict Annual Best Addition Current Candidate

## 한 줄 요약

현재 `Quality + Value > Strict Annual` bounded one-factor addition search에서
가장 좋은 practical addition 결과는 `per`였다.

이 조합은 baseline 대비

- `CAGR`를 높이고
- `MDD`를 개선하고
- gate도 한 단계 올렸다

는 점에서, current strongest blended candidate로 읽을 수 있다.

## 전략

- family: `Quality + Value`
- variant: `Strict Annual`
- role:
  - bounded addition search reference
  - current strongest practical blended candidate

## 전략 구성

### 기간 / universe

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`

### 핵심 설정

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

### factor 조합

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

### real-money / guardrail

- benchmark-relative practical contract defaults 유지
- underperformance guardrail `on`
- drawdown guardrail `on`

## 결과

- `CAGR = 29.43%`
- `MDD = -27.43%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation = normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

## 왜 다시 볼 가치가 있나

- baseline 대비 `CAGR`를 조금 더 끌어올렸다.
- `MDD`도 같이 개선했다.
- gate가 실제로 한 단계 올라갔다.
- 즉 blended family에서 current code 기준으로
  실제 승격까지 동반한 first-pass addition candidate다.

## 주의점

- `Deployment`는 여전히 `review_required`다.
- 즉 stronger candidate이긴 하지만,
  곧바로 완성형 live candidate라고 보긴 어렵다.
- 다음 단계는 이 조합을 anchor로 두고
  downside-improvement와 robustness search를 이어가는 것이다.

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
