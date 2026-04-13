# Phase 15 Quality + Value Strongest Anchor Top-N Search Sixth Pass

## 목적

quality-side fifth pass에서 새 strongest practical point가

- quality:
  - `net_margin -> operating_margin`
- value:
  - `ocf_yield -> pcr`
- `Top N = 10`
- `Candidate Universe Equal-Weight`

조합으로 갱신됐다.

이번 sixth pass에서는 이 new anchor 위에서
`Top N`만 다시 흔들어도 더 나은 practical candidate가 나오는지 확인한다.

## 고정 anchor

- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- quality:
  - `roe`
  - `roa`
  - `operating_margin`
  - `asset_turnover`
  - `current_ratio`
- value:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `operating_income_yield`
  - `per`
- benchmark:
  - `Candidate Universe Equal-Weight`
- overlays:
  - `Trend Filter = off`
  - `Market Regime = off`
- practical `Real-Money Contract`
- underperformance / drawdown guardrail `on`

## 실험 범위

- `Top N = 8`
- `Top N = 9`
- `Top N = 10`
- `Top N = 11`
- `Top N = 12`

## 결과

| Top N | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Rolling | OOS |
| ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| 8 | 32.47% | -30.79% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| 9 | 31.08% | -25.61% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| 10 | 31.25% | -26.63% | `real_money_candidate` | `small_capital_trial` | `review_required` | `normal` | `normal` | `normal` |
| 11 | 28.45% | -28.83% | `production_candidate` | `watchlist` | `review_required` | `watch` | `normal` | `normal` |
| 12 | 27.17% | -27.40% | `hold` | `hold` | `blocked` | `caution` | `normal` | `normal` |

## 해석

### 1. `Top N = 10`이 여전히 strongest practical point다

새 anchor를 기준으로 봐도:

- `Top N = 8`
  - `CAGR`는 가장 높지만
  - `validation = watch`
  - `production_candidate / watchlist`
  로 내려간다
- `Top N = 9`
  - `MDD`는 개선되지만
  - 여전히 `production_candidate / watchlist`
  다
- `Top N = 11`
  - 수익률과 낙폭이 둘 다 애매해지고
  - gate도 한 단계 내려간다
- `Top N = 12`
  - 바로 `hold / blocked`
  로 무너진다

즉 current practical gate와 성과를 같이 보면
`Top N = 10`이 가장 균형이 좋다.

### 2. `Top N = 9`는 notable lower-drawdown alternative다

`Top N = 9`는

- `CAGR = 31.08%`
- `MDD = -25.61%`

로 숫자만 보면 상당히 좋다.

다만:

- `Promotion = production_candidate`
- `Shortlist = watchlist`

라서 strongest practical point로 승격시키긴 어렵다.

### 3. sixth pass 결론

현재 `Quality + Value` strongest practical point는 유지된다.

- quality:
  - `net_margin -> operating_margin`
- value:
  - `ocf_yield -> pcr`
- `Top N = 10`
- `Candidate Universe Equal-Weight`

즉 fifth pass에서 찾은 strongest point는
이번 `Top N` follow-up에서도 깨지지 않았다.

## 다음 액션

1. current strongest point를 그대로 유지
2. Phase 15 current strongest candidates 정리를 마무리
3. 필요하면 다음 phase에서는
   stronger blended point 위에서만 bounded benchmark/overlay 실험을 다시 연다

## 관련 문서

- [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
