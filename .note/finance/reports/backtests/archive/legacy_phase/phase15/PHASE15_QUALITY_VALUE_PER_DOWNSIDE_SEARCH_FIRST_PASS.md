# Phase 15 Quality Value PER Downside Search First Pass

## 목적

`Quality + Value > Strict Annual` current strongest blended candidate인
`per` addition 조합을 anchor로 두고,

- `Top N`

만 바꿔도 더 나은 downside / gate tradeoff가 나오는지 확인한다.

이번 pass의 질문은 단순하다.

- `Top N = 10 + per`가 이미 가장 좋은 practical point인가
- 아니면 더 넓히거나 더 좁혀서
  `MDD`를 낮추거나 gate를 더 지킬 수 있는가

## 고정 계약

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Rebalance Interval = 1`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- factor 조합:
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

## 탐색 범위

- `Top N`:
  - `6`
  - `7`
  - `8`
  - `9`
  - `10`
  - `11`
  - `12`
  - `14`
  - `16`
  - `18`
  - `20`

## 결과 요약

| Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `6` | `30.77%` | `-29.94%` | `hold` | `hold` | `blocked` | `caution` | `watch` | `normal` |
| `7` | `32.28%` | `-31.67%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `8` | `31.69%` | `-27.64%` | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| `9` | `26.01%` | `-27.49%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `10` | `29.43%` | `-27.43%` | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| `11` | `27.85%` | `-28.62%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |
| `12` | `26.57%` | `-27.64%` | `hold` | `hold` | `blocked` | `caution` | `watch` | `normal` |
| `14` | `25.84%` | `-28.61%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| `16` | `23.87%` | `-27.46%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| `18` | `24.46%` | `-24.73%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |
| `20` | `24.65%` | `-24.60%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `normal` |

## 해석

- `Top N = 10`이 여전히 가장 좋은 practical point다.
  - 이번 pass에서 유일하게
    - `real_money_candidate`
    - `small_capital_trial`
    - `review_required`
    를 동시에 유지했다.
- `Top N = 8`과 `Top N = 7`은 수익률은 높았지만
  gate가 `production_candidate / watchlist`로 내려갔다.
- `Top N = 18`, `20`은 `MDD`는 더 낮아졌지만
  validation이 `caution`으로 바뀌면서 `hold / blocked`가 되었다.
- 즉 이 family에서는
  `Top N diversification`이 `Value` family에서처럼 downside-improvement lever로 잘 작동하지 않았다.

## 현재 판단

- `Quality + Value + per` current strongest candidate는 그대로
  `Top N = 10`이다.
- 다음 단계는 `Top N`보다
  - `factor replacement`
  - `quality-side pruning`
  - `benchmark / cadence sensitivity`
  같은 구조적 변화가 더 유효할 가능성이 높다.

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
