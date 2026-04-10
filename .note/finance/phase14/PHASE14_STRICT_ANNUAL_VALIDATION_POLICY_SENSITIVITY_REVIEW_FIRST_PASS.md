# Phase 14 Strict Annual Validation Policy Sensitivity Review First Pass

## 목적

- strict annual repeated `hold`의 대표 원인으로 좁혀진
  `validation_status`, `validation_policy_status`를
  **configurable threshold와 fixed internal threshold로 분리해서** 다시 읽는다.
- 특히 Phase 13 near-miss에서 가장 중요했던 질문,
  **"validation policy만 완화하면 hold가 풀리는가?"**
  에 current rerun evidence로 답하는 문서다.

## 한 줄 결론

- strict annual exact-hit hold에서는
  **`validation_policy` 완화만으로는 `hold`가 잘 풀리지 않는다.**
- 이유는 current gate가 `validation_policy_status`보다
  **fixed internal `validation_status`를 더 직접적인 1차 gate로 사용하기 때문**이다.

## 근거 코드

- `app/web/runtime/backtest.py::_build_real_money_validation_surface`
- `app/web/runtime/backtest.py::_build_validation_policy_surface`
- `app/web/runtime/backtest.py::_build_promotion_decision`

## 1. Current code path 정리

### 1-1. `validation_status`

`validation_status`는 benchmark-relative internal review layer다.
현재 기준은 아래와 같다.

- rolling window:
  - daily면 `252D`
  - month-end summary면 `12M`
- watch signals:
  - strategy max drawdown이 benchmark보다 `5%p` 이상 더 나쁠 때
  - worst rolling excess가 `-10%` 이하일 때
  - current underperformance streak가 `3` 이상일 때
  - underperformance share가 `60%` 이상일 때
- severe signals:
  - strategy max drawdown이 benchmark보다 `10%p` 이상 더 나쁠 때
  - worst rolling excess가 `-15%` 이하일 때
  - current underperformance streak가 `4` 이상일 때
- 판정:
  - severe signal이 하나라도 있거나 watch signal이 `2`개 이상이면 `caution`
  - watch signal만 있으면 `watch`
  - 없으면 `normal`

즉 이 layer는 **operator 입력값이 아니라 현재 코드에 고정된 gate**다.

### 1-2. `validation_policy_status`

`validation_policy_status`는 operator가 조절 가능한 policy layer다.
현재 contract는 아래 두 값이다.

- `promotion_max_underperformance_share`
- `promotion_min_worst_rolling_excess_return`

판정 방식:

- benchmark unavailable 또는 rolling observation이 없으면 `unavailable`
- share가 policy보다 높으면 watch / severe
- worst rolling excess가 policy보다 낮으면 watch / severe
- severe signal이 있으면 `caution`
- watch signal만 있으면 `watch`
- 없으면 `normal`

현재 default:

- `promotion_max_underperformance_share = 55%`
- `promotion_min_worst_rolling_excess_return = -15%`

### 1-3. `promotion_decision` 연결 경로

`_build_promotion_decision`에서 strict annual은 아래 조건이면 `hold`가 된다.

- `validation_status = caution`
- `validation_policy_status in {caution, unavailable}`
- `benchmark_policy_status = caution`
- `liquidity_policy_status in {caution, unavailable}`
- `guardrail_policy_status in {caution, unavailable}`
- `price_freshness.status = error`

즉 strict annual에서는
`validation_status`와 `validation_policy_status`가 **둘 다 실제 hold gate**다.

## 2. Representative rerun A: Value exact-hit hold

대상 케이스:

- family: `Value > Strict Annual`
- preset: `US Statement Coverage 100`
- universe: `Historical Dynamic PIT Universe`
- period: `2016-01-01 ~ 2026-04-01`
- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `top_n = 9`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- benchmark: `SPY`

baseline current rerun:

- `promotion = hold`
- `validation = caution`
- `validation_policy = caution`
- `rolling_underperformance_share = 36.61%`
- `rolling_underperformance_worst_excess_return = -39.39%`
- `validation_watch_signals = ['worst_excess']`
- `validation_policy_watch_signals = ['worst_rolling_excess_below_policy']`

### sensitivity: `promotion_min_worst_rolling_excess_return`

같은 케이스를 아래처럼 다시 돌렸다.

| `Min Worst Rolling Excess` | `validation_policy` | `validation` | `promotion` |
| --- | --- | --- | --- |
| `-15%` | `caution` | `caution` | `hold` |
| `-25%` | `caution` | `caution` | `hold` |
| `-40%` | `normal` | `caution` | `hold` |
| `-45%` | `normal` | `caution` | `hold` |

읽는 법:

- 이 케이스는 `underperformance_share`는 이미 default policy(`55%`)를 통과한다.
- current blocker는 거의 전부 `worst rolling excess` 쪽이다.
- 하지만 policy를 `-40%`까지 완화해도
  **fixed internal `validation_status = caution`이 그대로 남기 때문에 promotion은 계속 `hold`**다.

## 3. Representative rerun B: Quality capital-discipline near miss

대상 케이스:

- family: `Quality > Strict Annual`
- preset: `US Statement Coverage 100`
- universe: `Historical Dynamic PIT Universe`
- period: `2016-01-01 ~ 2026-04-01`
- factors:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- `top_n = 10`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = off`
- `drawdown_guardrail = off`
- benchmark: `SPY`

baseline current rerun:

- `promotion = hold`
- `validation = caution`
- `validation_policy = watch`
- `rolling_underperformance_worst_excess_return = -18.21%`
- `validation_watch_signals = ['worst_excess']`
- `validation_policy_watch_signals = ['worst_rolling_excess_below_policy']`

### sensitivity: `promotion_min_worst_rolling_excess_return`

| `Min Worst Rolling Excess` | `validation_policy` | `validation` | `promotion` |
| --- | --- | --- | --- |
| `-15%` | `watch` | `caution` | `hold` |
| `-25%` | `normal` | `caution` | `hold` |
| `-40%` | `normal` | `caution` | `hold` |
| `-45%` | `normal` | `caution` | `hold` |

읽는 법:

- quality near-miss는 policy layer를 완화하면 `validation_policy`는 바로 정상화된다.
- 그래도 `validation_status`가 `caution`에 남기 때문에
  **현재 strict annual hold를 풀 핵심 레버는 policy보다 internal validation threshold**에 더 가깝다.

## 4. First-pass 해석

### 4-1. 현재 configurable sensitivity knob

strict annual operator가 현재 직접 조절할 수 있는 validation-family knob는 아래다.

- `promotion_max_underperformance_share`
- `promotion_min_worst_rolling_excess_return`

이 둘은 `validation_policy_status`만 바꾼다.

### 4-2. 현재 code-level sensitivity knob

실제 repeated `hold`를 더 직접적으로 좌우하는 fixed internal knob는 아래다.

- drawdown gap watch:
  - `5%p`
- drawdown gap severe:
  - `10%p`
- worst rolling excess watch:
  - `-10%`
- worst rolling excess severe:
  - `-15%`
- current underperformance streak watch:
  - `3`
- current underperformance streak severe:
  - `4`
- underperformance share watch:
  - `60%`
- watch signal `2`개 이상이면 자동 `caution`

즉 current strict annual calibration은
**policy relaxation보다 internal validation threshold review가 더 영향력이 큰 구조**다.

## 5. Candidate calibration knobs

이번 first pass 기준으로 다음 실험 후보는 아래 순서가 맞다.

1. `worst_excess` severe boundary
   - current: `-15%`
   - 이유:
     - representative near-miss 두 건이 모두 여기서 `validation = caution`을 만든다.

2. watch-signal aggregation rule
   - current: `watch signal 2개 이상 -> caution`
   - 이유:
     - strict annual family가 multi-signal aggregation에 민감할 수 있다.

3. drawdown-gap severe boundary
   - current: `10%p`
   - 이유:
     - quality / quality+value defensive case에서 benchmark-relative drawdown 해석이 결과를 바꿀 가능성이 있다.

4. `promotion_min_worst_rolling_excess_return`
   - current: `-15%`
   - 이유:
     - policy layer 자체도 너무 tight한 case는 존재하지만,
       이번 evidence 기준 우선순위는 internal validation보다 낮다.

## 6. 결론

- strict annual current gate에서 repeated `hold`를 풀기 위한 핵심 질문은
  **"validation policy를 얼마나 느슨하게 하느냐"보다
  "internal validation caution을 어떤 evidence에서 허용/완화할 것이냐"** 에 더 가깝다.
- 따라서 다음 calibration 작업은
  blanket relaxation이 아니라
  **`validation_status` fixed threshold review first**
  방향으로 가는 것이 맞다.
