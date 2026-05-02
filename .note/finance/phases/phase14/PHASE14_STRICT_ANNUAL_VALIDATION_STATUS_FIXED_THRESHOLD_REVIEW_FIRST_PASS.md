# Phase 14 Strict Annual Validation Status Fixed-Threshold Review First Pass

## 목적

- Phase 14 sensitivity review 다음 단계로,
  strict annual repeated `hold`를 만드는
  **internal `validation_status` 고정 threshold**를 별도로 읽는다.
- 특히 아래 질문에 답하기 위한 문서다.
  - 왜 `validation_policy`를 완화해도 `hold`가 그대로 남는가?
  - strict annual에서 먼저 다시 봐야 할 fixed threshold는 무엇인가?

## 이번 문서의 한 줄 결론

- strict annual repeated `hold`의 가장 직접적인 current blocker는
  **`worst rolling excess <= -15%`가 single severe signal만으로도 `validation = caution`을 만드는 구조**다.
- 즉 다음 calibration 실험은
  `validation_policy` 완화보다
  **internal `validation_status` severe / caution 규칙**을 다시 보는 쪽이 더 직접적이다.

## 근거 코드

- `app/web/runtime/backtest.py::_build_real_money_validation_surface`
- `app/web/runtime/backtest.py::_build_promotion_decision`

## 1. Current fixed threshold inventory

현재 strict annual `validation_status`는 아래 internal rule로 만들어진다.

### watch signal

- strategy max drawdown이 benchmark보다 `5%p` 이상 더 나쁠 때
- `worst rolling excess <= -10%`
- `current underperformance streak >= 3`
- `underperformance share >= 60%`

### severe signal

- strategy max drawdown이 benchmark보다 `10%p` 이상 더 나쁠 때
- `worst rolling excess <= -15%`
- `current underperformance streak >= 4`

### 판정 규칙

- severe signal이 하나라도 있으면 `validation = caution`
- severe가 없어도 watch signal이 `2`개 이상이면 `validation = caution`
- watch signal만 있으면 `validation = watch`
- 없으면 `validation = normal`

즉 current strict annual gate는
**single severe signal 하나만으로도 바로 `caution`으로 올라가는 구조**다.

## 2. Representative evidence

### Case A. Value exact-hit hold

대상:

- `Value > Strict Annual`
- `earnings_yield / ocf_yield / operating_income_yield / fcf_yield`
- `2016-01-01 ~ 2026-04-01`
- `top_n = 9`
- `trend_filter = on`
- `market_regime = on`
- benchmark: `SPY`

결과:

- `CAGR = 15.84%`
- `MDD = -17.42%`
- `promotion = hold`
- `validation = caution`
- `validation_policy = caution`
- `rolling_underperformance_share = 36.61%`
- `rolling_underperformance_worst_excess_return = -39.39%`
- `validation_watch_signals = ['worst_excess']`

해석:

- `underperformance_share`는 current policy 기준에서도 이미 통과한다.
- current blocker는 사실상 `worst_excess` 하나다.
- 그리고 이 값이 `-15%` severe boundary보다 훨씬 나쁘기 때문에,
  current logic에서는 **single severe signal만으로 `validation = caution`**이 만들어진다.

### Case B. Quality capital-discipline near miss

대상:

- `Quality > Strict Annual`
- `roe / roa / cash_ratio / debt_to_assets`
- `2016-01-01 ~ 2026-04-01`
- `top_n = 10`
- `trend_filter = on`
- `market_regime = on`
- benchmark: `SPY`

결과:

- `CAGR = 15.80%`
- `MDD = -27.97%`
- `promotion = hold`
- `validation = caution`
- `validation_policy = watch`
- `rolling_underperformance_worst_excess_return = -18.21%`
- `validation_watch_signals = ['worst_excess']`

해석:

- quality near-miss도 같은 패턴이다.
- policy layer는 `watch` 수준인데,
  internal `worst_excess <= -15%`가 이미 severe라
  `validation = caution`이 먼저 고정된다.

## 3. 지금 무엇이 1차 blocker인가

현재 evidence 기준으로 strict annual repeated hold를 더 직접적으로 좌우하는 순서는 이렇다.

### 1순위

- `worst rolling excess` severe boundary `-15%`

이유:

- representative value / quality near-miss 두 건이 모두 여기서 바로 severe가 된다.
- current policy를 완화해도 internal `validation`은 그대로 남는다.

### 2순위

- `single severe signal -> automatic caution` 규칙

이유:

- 지금은 다른 watch signal이 거의 없어도
  severe 하나만 있으면 바로 `caution`이다.
- strict annual family에서는 이 구조가 너무 보수적일 가능성을 점검할 가치가 있다.

### 3순위

- drawdown gap watch/severe 경계
  - watch `5%p`
  - severe `10%p`

이유:

- current 대표 케이스에선 1차 blocker가 아니었지만,
  family 전반 calibration에서는 다음 후보로 읽힌다.

### 우선순위 낮음

- underperformance share `60%`
- current underperformance streak `3 / 4`

이유:

- current exact-hit hold와 quality near-miss에선
  이 항목들이 직접적인 blocker로 먼저 보이지 않았다.

## 4. 다음 calibration experiment 후보

이번 first pass 기준으로 다음 실험 후보는 아래 순서가 자연스럽다.

1. `worst_excess` severe boundary review
   - current: `-15%`
   - 질문:
     - strict annual에서는 `-20%` 또는 `-25%`가 더 현실적인가?

2. `single severe signal` 해석 review
   - current:
     - severe 하나만 있어도 자동 `caution`
   - 질문:
     - strict annual에서는 severe 1개 + 추가 watch signal이 있을 때만 `caution`으로 올릴지 검토할 가치가 있는가?

3. drawdown gap fixed threshold review
   - current:
     - watch `5%p`
     - severe `10%p`
   - 질문:
     - strict annual family의 benchmark-relative downside 해석에 맞는가?

## 5. 이번 단계에서 아직 하지 않는 것

- blanket threshold relaxation
- `validation_policy`와 `validation_status`를 한 번에 같이 완화
- ETF family와 strict annual family를 같은 fixed threshold로 다시 묶는 작업

## 한 줄 결론

strict annual next calibration은
**operator-facing `validation_policy`보다 internal `validation_status` fixed threshold를 먼저 보는 단계**다.

특히 current evidence 기준으로는
`worst rolling excess <= -15%`와
`single severe signal -> caution` 규칙이
가장 먼저 검토할 후보다.
