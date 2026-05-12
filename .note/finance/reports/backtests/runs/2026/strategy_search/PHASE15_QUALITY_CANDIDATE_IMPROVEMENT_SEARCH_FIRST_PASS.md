# Phase 15 Quality Candidate Improvement Search First Pass

## 목적

`Quality > Strict Annual` family에서 current strict annual practical contract 기준으로
bounded single-factor addition이 `hold`를 벗어나는 practical candidate를 만들 수 있는지 확인한다.

이번 pass는 특히:

- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`
- literal preset semantics

기준으로 다시 돌려, 예전 non-hold reference가 현재 코드에서도 유지되는지 함께 점검했다.

## 고정 계약

- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Benchmark Contract = Ticker Benchmark`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = on`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- anchor factor:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`

## 탐색 범위

- anchor rerun
- single-factor additions only:
  - `interest_coverage`
  - `ocf_margin`
  - `fcf_margin`
  - `net_debt_to_equity`

## 결과 요약

| Case | Factors | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| baseline | `roe, roa, cash_ratio, debt_to_assets` | `13.26%` | `-32.59%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `watch` |
| `+ interest_coverage` | `roe, roa, cash_ratio, debt_to_assets, interest_coverage` | `15.74%` | `-34.18%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `caution` |
| `+ ocf_margin` | `roe, roa, cash_ratio, debt_to_assets, ocf_margin` | `6.83%` | `-31.90%` | `hold` | `hold` | `blocked` | `caution` | `watch` | `caution` |
| `+ fcf_margin` | `roe, roa, cash_ratio, debt_to_assets, fcf_margin` | `7.95%` | `-27.60%` | `hold` | `hold` | `blocked` | `caution` | `watch` | `caution` |
| `+ net_debt_to_equity` | `roe, roa, cash_ratio, debt_to_assets, net_debt_to_equity` | `13.51%` | `-23.84%` | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |

## 해석

- 이번 bounded search에서는 `Promotion != hold` 후보가 하나도 나오지 않았다.
- 즉 `Quality` family는 current literal preset semantics 기준으로 보면,
  single-factor addition만으로는 practical non-hold candidate를 회복하지 못했다.
- 가장 균형이 나았던 near-miss는 `net_debt_to_equity` addition이다.
  - `MDD`는 가장 크게 개선됐지만
  - `validation_status = caution`이 그대로라 `hold / blocked`를 못 벗어났다.
- `interest_coverage`는 `CAGR`는 약간 좋아졌지만 `MDD`와 `OOS`가 더 나빠졌다.
- `ocf_margin`, `fcf_margin`은 방어적일 수 있다는 기대와 달리
  이번 계약에서는 validation / OOS를 더 약하게 만들었다.

## 현재 판단

- `Quality > Strict Annual`은 현재 phase 기준으로
  factor one-addition만으로는 회복되지 않는 family다.
- 다음 액션은
  - `benchmark rescue`
  - `overlay on/off reset`
  - `factor replacement`
  - `Top N / rebalance interval`
  같은 bounded structural search로 넘어가는 쪽이 더 맞다.

## 관련 문서

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase14/PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md)
