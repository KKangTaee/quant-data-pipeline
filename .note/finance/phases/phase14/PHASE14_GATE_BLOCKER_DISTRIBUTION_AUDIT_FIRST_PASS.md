# Phase 14 Gate Blocker Distribution Audit First Pass

## 목적

- `promotion = hold`, `deployment = blocked`가 반복될 때
  어떤 gate가 실제로 가장 자주 막는지 first-pass 기준으로 정리한다.
- 이번 문서는 아직 full telemetry aggregate가 아니라,
  **current code gate logic + Phase 13 representative candidate 문서 + history persistence gap 확인**
  을 함께 묶은 audit이다.

## 이번 first-pass에서 확인한 한계

- 기존 `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl` record는
  실행 입력과 primary summary는 남기지만,
  `promotion / shortlist / deployment / validation policy` 상태를 같이 저장하지 않았다.
- 따라서 broad aggregate를 바로 계산하기보다는,
  Phase 13에서 이미 정리된 대표 candidate 문서와 current code gate logic을 기준으로
  blocker distribution을 먼저 정리하는 것이 더 정확했다.
- 이번 work unit에서는 이 한계를 줄이기 위해
  **history schema v2에 `gate_snapshot` 저장을 추가**했다.
- 다만 기존 history `218`개 record는 여전히 legacy shape라서,
  이번 문서의 수치 분포는 **legacy history aggregate가 아니라 representative rerun set** 기준이다.

## 근거 코드

- `app/web/runtime/backtest.py::_build_promotion_decision`
- `app/web/runtime/backtest.py::_build_shortlist_contract`
- `app/web/runtime/backtest.py::_build_probation_and_monitoring_contract`
- `app/web/runtime/backtest.py::_build_deployment_readiness_contract`

현재 `promotion = hold`를 직접 만드는 조건은 아래다.

- `benchmark_available = False`
- `validation_status = caution`
- `benchmark_policy_status = caution`
- `etf_operability_status in {caution, unavailable}`
- `liquidity_policy_status in {caution, unavailable}`
- `validation_policy_status in {caution, unavailable}`
- `guardrail_policy_status in {caution, unavailable}`
- `price_freshness.status = error`

즉 current gate는
`watch` 수준은 `production_candidate`로 흡수할 수 있지만,
`caution / unavailable / error`는 기본적으로 `hold` 쪽으로 밀어낸다.

## 2026-04-09 representative rerun set

이번 first-pass는 아래 `9`개 대표 케이스를 current runtime code로 다시 실행해 상태를 고정했다.

| 케이스 | Family | 결과 상태 | 대표 blocker |
| --- | --- | --- | --- |
| `value_raw_winner` | Value strict annual | `real_money_candidate / paper_probation / review_required` | blocker 없음, 다만 `rolling = watch`, `oos = caution` |
| `value_balanced_near_miss` | Value strict annual | `hold / hold / blocked` | `validation_caution`, `validation_policy_caution` |
| `quality_capital_discipline` | Quality strict annual | `hold / hold / blocked` | `validation_caution`, `validation_policy_caution`, `guardrail_policy_watch` |
| `quality_value_defensive_nonhold` | Quality + Value strict annual | `production_candidate / watchlist / review_required` | `validation_watch` |
| `quality_value_low_drawdown_hold` | Quality + Value strict annual | `hold / hold / blocked` | `validation_caution`, `benchmark_policy_caution`, `validation_policy_caution` |
| `gtaa_practical_nonhold` | GTAA | `production_candidate / watchlist / watchlist_only` | `validation_watch` |
| `gtaa_aggressive_near_miss` | GTAA | `hold / hold / blocked` | `validation_watch`, `etf_operability_caution` |
| `risk_parity_default` | Risk Parity Trend | `hold / hold / blocked` | `validation_caution` |
| `dual_momentum_default` | Dual Momentum | `hold / hold / blocked` | `validation_caution`, `etf_operability_caution` |

요약 분포:

- `real_money_candidate`: `1 / 9`
- `production_candidate`: `2 / 9`
- `hold`: `6 / 9`
- `review_required`: `2 / 9`
- `watchlist_only`: `1 / 9`
- `blocked`: `6 / 9`

hold `6`건만 놓고 보면, 반복된 강한 blocker는 아래 순서였다.

- `validation_status = caution`: `5 / 6`
- `validation_policy_status = caution`: `3 / 6`
- `etf_operability_status = caution`: `2 / 6`
- `benchmark_policy_status = caution`: `1 / 6`
- `liquidity_policy_status = caution/unavailable`: `0 / 6`
- `price_freshness.status = error`: `0 / 6`

즉 current representative set에서는
`liquidity`나 `price freshness`보다
**`validation / validation_policy / ETF operability`가 훨씬 더 자주 hold를 만든다.**

## 대표 candidate 기준 first-pass blocker 분포

### 1. Strict Annual family

대표 문서:

- `.note/finance/backtest_reports/phase13/PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md`
- `.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH.md`
- `.note/finance/backtest_reports/phase13/PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md`
- `.note/finance/backtest_reports/phase13/PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md`
- `.note/finance/backtest_reports/phase13/PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH.md`

current rerun 기준 관찰 패턴:

1. `Value` strongest raw winner는 지금도 `real_money_candidate`까지 재현된다.
2. 하지만 drawdown을 줄인 balanced near-miss나 `Quality` family 후보는
   여전히 `hold`에 남는다.
3. `Quality + Value`는 benchmark를 `LQD`처럼 더 방어적으로 바꾸면
   `production_candidate / watchlist`까지 올라갈 수 있다.

가장 자주 반복된 blocker:

- `validation_status = caution`
- `validation_policy_status = caution`
- `rolling_review_status = caution`

대표 근거:

- `PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH`
  - `CAGR = 15.84%`, `MDD = -17.42%`
  - 숫자 조건은 맞았지만 `promotion = hold`
  - 직접 원인:
    - `validation_status = caution`
    - `validation_policy_status = caution`
    - `rolling_underperformance_worst_excess_return = -39.4%`
- `PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH`
  - `capital_discipline` current rerun
  - `validation = caution`, `validation_policy = caution`, `guardrail_policy = watch`, `out_of_sample = caution`
  - 즉 strict annual quality는 현재도
    **benchmark-relative validation 자체가 먼저 막는 경우**가 확인됐다.
- `PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH`
  - 같은 defensive factor 구조에서도 `benchmark = SPY`일 때는 대부분 `hold`
  - `benchmark = LQD`로 바꾸면 일부가 `production_candidate`
  - 즉 `Quality + Value`는 validation family blocker가 남아 있지만,
    **benchmark-relative threshold 해석이 결과를 크게 바꾼다.**

추가로 중요한 점:

- `value_raw_winner`는 `rolling = watch`, `oos = caution`이어도
  `promotion = real_money_candidate`가 유지됐다.
- 즉 current promotion gate는
  `rolling / out-of-sample`을 직접 hold로 만들기보다,
  **`validation_status`와 `validation_policy_status`를 더 직접적인 1차 gate로 사용한다.**

### 2. ETF family

대표 문서:

- `.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md`
- `.note/finance/backtest_reports/strategies/GTAA.md`

current rerun 기준 관찰 패턴:

1. practical GTAA candidate는 지금도
   `Promotion = production_candidate`, `Deployment = watchlist_only`
   까지 안정적으로 재현된다.
2. ETF family는 strict annual과 달리,
   `validation = watch` 상태에서도 `hold`를 벗어나는 practical case가 이미 있다.
3. 대신 더 공격적인 ETF candidate는
   **`ETF operability` current-data gap** 때문에 `hold`로 밀릴 수 있다.
4. `Risk Parity Trend`, `Dual Momentum` default는 현재 representative contract 기준으로는
   둘 다 `hold / blocked` 상태다.

대표 근거:

- practical GTAA:
  - `SPY, QQQ, GLD, LQD`
  - `top = 2`, `interval = 3`, `score horizons = 1M / 3M`
  - `Promotion = production_candidate`
  - `Deployment = watchlist_only`
  - `Validation = watch`
  - `ETF Operability = normal`
- aggressive GTAA near-miss:
  - 더 높은 `CAGR`와 양호한 `MDD`를 보였지만
  - current rerun에서도 `validation = watch`인데 `etf_operability = caution`이 붙으면서
    `promotion = hold`가 됐다.
- `Risk Parity Trend` default:
  - `validation = caution`
  - `rolling = caution`
  - `out_of_sample = caution`
  - `etf_operability = normal`
- `Dual Momentum` default:
  - `validation = caution`
  - `etf_operability = caution`
  - `out_of_sample = caution`

즉 ETF family의 blocker는 strict annual처럼 `validation_caution`이 절대적이라기보다,
**operability current-state gate와 validation watch/caution 해석이 함께 작동하는 구조**로 보인다.

## First-Pass 결론

### Strict Annual

- repeated `hold`의 1차 blocker는
  **`validation / validation_policy / rolling underperformance`**
  쪽이다.
- `liquidity_policy`, `guardrail_policy`는 current strict annual near-miss에서
  주 blocker로 반복되기보다,
  validation family가 먼저 막는 패턴이 더 강했다.

### ETF

- ETF family는 이미 `production_candidate / watchlist_only` practical case가 존재한다.
- ETF repeated blocker는 strict annual보다
  **`ETF operability`와 practical validation 해석** 쪽이 더 중요하다.
- 다만 ETF family도 전체적으로 느슨한 것은 아니다.
  current representative set에서는
  `GTAA practical candidate`만 non-hold였고,
  `Risk Parity Trend`, `Dual Momentum`, `GTAA` 공격형 후보는 모두 `hold`였다.

### 공통

- current gate는 “좋은 숫자”보다
  “benchmark-relative consistency와 operability까지 같이 clean한가”를 더 강하게 본다.
- 따라서 repeated `hold`는 단순 alpha 부족이 아니라
  **현재 gate가 보수적으로 잘 작동하는 결과**일 가능성이 높다.
- 동시에, 이 보수성이 family마다 타당하게 calibrated되어 있는지는
  이번 phase에서 추가 검토가 필요하다.
- current rerun evidence 기준으로 보면,
  blanket relaxation보다 먼저 볼 대상은 아래다.
  - strict annual: `validation_status`, `validation_policy_status`
  - ETF: `etf_operability_status`와 `validation watch/caution` 경계

## 이번 first-pass에서 바로 생긴 구현 결정

- 이후 audit evidence를 쌓기 위해
  `BACKTEST_RUN_HISTORY.jsonl` schema를 `v2`로 올리고,
  다음 상태를 `gate_snapshot`으로 함께 저장한다.
  - `promotion`
  - `shortlist`
  - `probation`
  - `monitoring`
  - `deployment`
  - `validation / benchmark / liquidity / validation_policy / guardrail / etf_operability`
  - `rolling / out_of_sample`
  - `price_freshness`

즉 앞으로는 representative report에만 의존하지 않고,
실행 history 자체에서 blocker distribution을 더 직접 집계할 수 있게 된다.

## 다음 단계

1. 새 schema로 쌓이는 history record를 기준으로
   blocker frequency를 실제 aggregate로 다시 계산한다.
2. 아래 `4`개를 canonical calibration case로 고정한다.
   - `Value` raw winner
   - `Value` balanced near-miss
   - `Quality + Value` defensive non-hold
   - `GTAA` practical non-hold
3. family별로 아래 threshold를 분리 검토한다.
   - `promotion_max_underperformance_share`
   - `promotion_min_worst_rolling_excess_return`
   - `promotion_min_benchmark_coverage`
   - `promotion_min_liquidity_clean_coverage`
4. ETF operability는 snapshot overlay와 actual block rule 사이의
   contract boundary를 다시 문서화한다.
