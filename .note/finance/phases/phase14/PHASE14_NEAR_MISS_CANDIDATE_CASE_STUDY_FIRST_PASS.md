# Phase 14 Near-Miss Candidate Case Study First Pass

## 목적

- Phase 14 calibration review를 추상적인 threshold inventory 수준에서 멈추지 않고,
  실제 representative candidate가 어떤 이유로 `hold`, `watchlist`, `watchlist_only`에 머무는지
  **케이스 단위로 다시 읽는다.**
- 특히 아래 질문에 답하기 위한 문서다.
  - strong absolute performance인데 왜 `hold`인가?
  - non-hold인데 왜 `paper_probation` 이상으로 못 가는가?
  - strict annual과 ETF family의 near-miss 패턴은 어떻게 다른가?

## 이번 문서의 한 줄 결론

- strict annual near-miss는 주로 **validation / validation_policy**에서 막히고,
  ETF near-miss는 **validation watch/caution 경계 + ETF operability**가 함께 작동한다.
- 따라서 다음 calibration 실험도 blanket relaxation이 아니라
  **family별로 다른 문턱을 정밀하게 보는 방향**이 맞다.

## 대표 케이스

이번 first pass는 아래 네 케이스를 Phase 13 대표 report + Phase 14 rerun evidence 기준으로 다시 읽었다.

1. `Value strict annual` balanced exact-hit hold
2. `Quality strict annual` SPY-dominance near miss
3. `GTAA` practical non-hold
4. `GTAA` aggressive near miss

---

## Case 1. Value strict annual balanced exact-hit hold

### 설정

- family: `Value > Strict Annual`
- universe: `Historical Dynamic PIT Universe`
- period: `2016-01-01 ~ 2026-04-01`
- `top_n = 9`
- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- benchmark: `SPY`

### 결과

- `CAGR = 15.84%`
- `MDD = -17.42%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `validation_policy = caution`
- `rolling = caution`
- `out_of_sample = normal`

### 왜 near-miss인가

- 숫자만 보면:
  - `CAGR >= 15%`
  - `MDD >= -20%`
  를 동시에 만족하는 exact hit였다.
- 그런데 current gate는 absolute performance보다
  **benchmark-relative consistency**를 더 강하게 보므로,
  이 케이스는 strong return profile에도 `hold`가 남았다.

### calibration 시사점

- strict annual에서 가장 먼저 봐야 하는 건
  `liquidity`나 `price freshness`가 아니라
  **`validation_status`, `validation_policy_status`가 어떻게 계산되는가**다.
- 즉 이 케이스는
  "좋은 전략인데 gate가 너무 빡빡하다"라고 단정하기보다는,
  **validation 문턱이 어느 정도일 때 strong candidate를 놓치는가**
  를 측정하는 기준 케이스로 쓰는 편이 맞다.

---

## Case 2. Quality strict annual SPY-dominance near miss

### 설정

- family: `Quality > Strict Annual`
- factor set: `capital_discipline`
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- period: `2016-01-01 ~ 2026-04-01`
- `top_n = 10`
- `trend_filter = on`
- `market_regime = on`
- benchmark: `SPY`

### 결과

- `CAGR = 15.80%`
- `MDD = -27.97%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `rolling = normal`
- `out_of_sample = normal`

### 왜 near-miss인가

- 이 케이스는 raw 숫자만 보면 `SPY` 대비 attractive해 보이지만,
  quality family에서는 current gate가 여전히 `hold`를 유지한다.
- 특히 `rolling`과 `out_of_sample`은 상대적으로 덜 나쁜데도
  `validation = caution`이 승격을 바로 막는다.

### calibration 시사점

- strict annual quality는
  **absolute quality narrative**보다
  **benchmark-relative validation scoring**에 더 민감하다.
- 따라서 quality family calibration은
  factor 확장보다 먼저
  - `validation = caution` 경계
  - `drawdown gap` 해석
  을 보는 편이 우선이다.

---

## Case 3. GTAA practical non-hold

### 설정

- family: `GTAA`
- tickers:
  - `SPY`
  - `QQQ`
  - `GLD`
  - `LQD`
- period: `2016-01-01 ~ 2026-04-02`
- `top = 2`
- `interval = 3`
- score horizons:
  - `1M`
  - `3M`
- benchmark: `SPY`
- `Min ETF AUM = 0.0`
- `Max Bid-Ask Spread = 100.0`

### 결과

- `CAGR = 14.7671%`
- `MDD = -11.5626%`
- `promotion = production_candidate`
- `shortlist = watchlist`
- `deployment = watchlist_only`
- `validation = watch`
- `etf_operability = normal`
- `rolling = normal`
- `out_of_sample = normal`

### 왜 near-miss인가

- 이 케이스는 `hold`는 벗어났지만,
  아직 `paper_probation` 이상으로는 가지 못한다.
- blocker는 `validation = watch` 수준이라,
  strict annual hold보다 훨씬 약한 편이다.

### calibration 시사점

- ETF family는 strict annual처럼
  `validation = caution`이 절대적으로 반복되기보다,
  practical candidate가 이미 `production_candidate`까지는 올라간다.
- 즉 ETF family calibration은 blanket loosen이 아니라
  **`watch -> paper_probation` 경계와 operability 조건**
  을 더 보는 편이 맞다.

---

## Case 4. GTAA aggressive near miss

### 설정

- family: `GTAA`
- tickers:
  - `SPY`
  - `QQQ`
  - `SOXX`
  - `VUG`
  - `VTV`
  - `RSP`
  - `IAU`
  - `XLE`
  - `TIP`
  - `TLT`
  - `IEF`
  - `LQD`
  - `VNQ`
  - `EFA`
  - `GLD`
- `top = 2`
- `interval = 3`
- score horizons:
  - `1M`
  - `3M`
  - `6M`
- benchmark: `SPY`

### 결과

- `CAGR = 16.7189%`
- `MDD = -13.0870%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = watch`
- `etf_operability = caution`

### 왜 near-miss인가

- 숫자는 practical GTAA보다 더 공격적으로 좋아 보였지만,
  **operability gate** 때문에 current contract에서는 `hold`가 남았다.
- 즉 ETF family에서는
  "성과가 좋으면 된다"가 아니라
  **current operability contract를 같이 만족해야 non-hold가 유지된다**는 점이 다시 확인됐다.

### calibration 시사점

- ETF aggressive candidate는
  strict annual처럼 validation policy가 아니라
  **AUM / spread / operability current-state 기준**에 더 민감하다.
- 따라서 ETF family에서는 다음 calibration 질문이 중요하다.
  - `Min ETF AUM` 기본값이 실제 practical contract에 맞는가?
  - `Max Bid-Ask Spread` current snapshot 해석이 너무 가혹한가?
  - `watch`와 `caution` 경계가 어떤 practical case를 놓치고 있는가?

---

## 케이스 비교 요약

| 케이스 | 숫자 profile | 현재 상태 | 핵심 blocker | 다음 calibration 질문 |
| --- | --- | --- | --- | --- |
| Value balanced exact-hit | strong | `hold / blocked` | `validation`, `validation_policy` | strict annual validation 문턱이 너무 빡빡한가 |
| Quality SPY-dominance | decent/strong | `hold / blocked` | `validation` | quality family validation scoring이 과보수적인가 |
| GTAA practical | practical | `production / watchlist_only` | `validation_watch` | ETF watch를 어디까지 shortlist로 올릴 것인가 |
| GTAA aggressive | strong | `hold / blocked` | `etf_operability_caution` | operability threshold가 너무 aggressive candidate를 막는가 |

## First-pass 운영 결론

### Strict Annual

- near-miss 케이스는 대부분
  **absolute number failure**가 아니라
  **validation family blocker**였다.
- 따라서 next calibration 실험은
  - `validation_status`
  - `validation_policy_status`
  - strict annual benchmark-relative consistency 문턱
  을 먼저 보는 게 자연스럽다.

### ETF

- practical non-hold가 이미 존재한다는 점에서
  gate가 구조적으로 너무 빡빡하다고 보긴 어렵다.
- 대신 공격형 후보가 `operability`에서 막히는 패턴이 분명하므로,
  ETF calibration은
  **current operability threshold와 watch/caution boundary**
  가 핵심이다.

## 다음 단계

이번 case study 다음으로 가장 자연스러운 active step은:

1. strict annual `validation / validation_policy` sensitivity review
2. ETF `operability` threshold sensitivity review
3. 그 다음 deployment workflow bridge로 넘어가기

## 한 줄 결론

strong 숫자를 보이는 near-miss가 계속 막히는 이유는
blanket over-conservative gate라기보다,
**strict annual은 validation 쪽, ETF는 operability 쪽 calibration 질문이 아직 남아 있기 때문**이다.
