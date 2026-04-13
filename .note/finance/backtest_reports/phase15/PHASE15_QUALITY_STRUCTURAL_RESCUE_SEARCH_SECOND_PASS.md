# Phase 15 Quality Structural Rescue Search Second Pass

## 목적

`Quality > Strict Annual` family에서
bounded single-factor addition만으로는 current non-hold candidate를 회복하지 못했기 때문에,

- `benchmark`
- `overlay`
- `Top N`

같은 구조 레버를 다시 조정했을 때
실제 practical candidate가 살아나는지 current code 기준으로 확인한다.

이번 pass의 질문은 단순하다.

- `Quality`는 아직도 `hold`에 머무는 family인가
- 아니면 구조 조합을 바꾸면
  `real_money_candidate / paper_probation`까지 회복되는가

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
- 실전형 계약:
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
  - underperformance / drawdown guardrail `on`

## 확인한 대표 구조 조합

| Case | Benchmark | Trend | Regime | Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `q_capital_discipline_lqd_on_on_t10` | `LQD` | `on` | `on` | `10` | `14.84%` | `-27.97%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `q_capital_discipline_lqd_on_off_t10` | `LQD` | `on` | `off` | `10` | `24.28%` | `-31.48%` | `real_money_candidate` | `paper_probation` | `review_required` | `normal` | `normal` | `normal` |
| `q_capital_discipline_plus_netdebt_lqd_on_off_t10` | `LQD` | `on` | `off` | `10` | `20.48%` | `-23.52%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `q_capital_discipline_spy_off_off_t10` | `SPY` | `off` | `off` | `10` | `17.22%` | `-34.72%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `caution` |

## 해석

- 이번 second pass의 핵심은 분명하다.
  - `Quality`는 더 이상 “무조건 hold인 family”가 아니다.
  - current practical contract 기준에서도
    구조 조합을 바꾸면 `real_money_candidate / paper_probation`까지 회복된다.
- 가장 좋은 rescue case는
  - `capital_discipline`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
  - `Top N = 10`
  이 조합이었다.
- 이 케이스는
  - `Validation = normal`
  - `Rolling = normal`
  - `OOS = normal`
  까지 맞아,
  현재 `Quality` family에서 가장 깨끗한 structural recovery 후보로 읽는 편이 맞다.
- 반대로 `+ net_debt_to_equity`는
  `MDD`는 더 낮췄지만
  `Validation = caution`으로 돌아가면서 `hold`를 못 벗어났다.
- `SPY` benchmark 유지 조합은 이번 pass에서
  current practical contract 기준으로는 여전히 `hold / blocked`였다.

## 현재 판단

- `Quality`의 다음 레버는 “factor를 더 붙이는 것”보다
  `benchmark / overlay` 구조를 적절히 고르는 쪽에 더 가깝다.
- 현재 strongest practical candidate는
  `q_capital_discipline_lqd_on_off_t10`이다.
- 따라서 다음 단계는
  - 이 rescued anchor 기준 downside / top_n 조정
  - 또는 bounded factor addition을 다시 붙였을 때
    `real_money_candidate`를 유지하는지 확인
  으로 이어가는 편이 맞다.

## 관련 문서

- [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
