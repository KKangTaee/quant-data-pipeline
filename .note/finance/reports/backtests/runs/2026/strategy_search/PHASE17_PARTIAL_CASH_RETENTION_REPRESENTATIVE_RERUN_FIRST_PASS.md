# Phase 17 Partial Cash Retention Representative Rerun First Pass

## 목적

Phase 17 first implementation slice로 추가한
`partial cash retention`이 실제 current anchor에서

- `MDD`를 의미 있게 낮추는지
- 그 과정에서 `Promotion / Shortlist / Deployment`를 유지할 수 있는지

를 representative rerun으로 확인한다.

## 왜 이런 방식으로 다시 보나

`partial cash retention`은
`Trend Filter`가 일부 종목만 탈락시킬 때만 실제로 작동한다.

즉:

- `Trend Filter = off` anchor를 그대로 다시 돌리면
  기능이 사실상 비활성 상태다
- 그래서 이번 representative rerun은
  `current anchor + Trend Filter = on + Market Regime = off`
  조합에서
  `cash retention off/on`을 나란히 비교하는 방식으로 잡았다

## 고정한 공통 계약

- 기간:
  - `2016-01-01 ~ 2026-04-01`
- preset:
  - `US Statement Coverage 100`
- `Universe Contract`:
  - `Historical Dynamic PIT Universe`
- practical contract:
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
- guardrail:
  - underperformance `on / 12M / -10%`
  - drawdown `on / 12M / -35% / 8%`
- overlay:
  - `Trend Filter = on`
  - `Market Regime = off`

## 대상 anchor

### 1. Value anchor

- family:
  - `Value > Strict Annual`
- factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `psr`
- `Top N = 14`
- `Benchmark Contract = Ticker Benchmark`
- `Benchmark Ticker = SPY`

### 2. Quality + Value strongest anchor

- family:
  - `Quality + Value > Strict Annual`
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
  - `por`
  - `per`
- `Top N = 10`
- `Benchmark Contract = Candidate Universe Equal-Weight`

## representative rerun summary

| Case | CAGR | MDD | Promotion | Shortlist | Deployment | Validation | Benchmark Policy | Liquidity Policy | Rolling | OOS | Partial Cash Active Rows | Avg Cash Share |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: |
| `Value anchor + trend on + cash off` | `25.92%` | `-29.25%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` | `normal` | `normal` | `0` | `11.38%` |
| `Value anchor + trend on + cash on` | `20.11%` | `-15.85%` | `hold` | `hold` | `blocked` | `watch` | `caution` | `caution` | `watch` | `normal` | `113` | `31.14%` |
| `Q+V strongest + trend on + cash off` | `30.01%` | `-29.72%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` | `normal` | `normal` | `0` | `11.40%` |
| `Q+V strongest + trend on + cash on` | `20.03%` | `-15.07%` | `hold` | `hold` | `blocked` | `caution` | `caution` | `caution` | `normal` | `normal` | `90` | `41.41%` |

## 읽는 법

### Value

- `cash retention on`은 실제로 작동했다
  - `113`개 리밸런싱 행에서 partial cash retention이 활성화됐다
- `MDD`는 크게 좋아졌다
  - `-29.25% -> -15.85%`
- 하지만 `CAGR`가 꽤 줄었다
  - `25.92% -> 20.11%`
- `validation`은 `caution -> watch`로 한 단계 좋아졌지만
  `benchmark_policy`와 `liquidity_policy`가 여전히 `caution`이라
  `Promotion = hold`를 못 벗어났다

쉽게 말하면:

- downside protection 효과는 분명히 있었다
- 하지만 현금 비중이 많이 남으면서
  return drag가 커졌고
- gate rescue까지 이어지진 않았다

### Quality + Value

- `cash retention on`도 실제로 작동했다
  - `90`개 리밸런싱 행에서 활성화됐다
- `MDD`는 크게 좋아졌다
  - `-29.72% -> -15.07%`
- 하지만 `CAGR`가 크게 줄었다
  - `30.01% -> 20.03%`
- `validation`은 여전히 `caution`이고
  `benchmark_policy`와 `liquidity_policy`도 `caution`이라
  practical gate는 그대로 `hold / blocked`에 머물렀다

쉽게 말하면:

- blended strongest point도
  partial cash retention만으로는
  same-gate lower-MDD candidate가 되지 못했다

## 결론

### 1. partial cash retention은 기능적으로는 유효하다

- 두 family 모두 실제로 활성화됐다
- `MDD`를 매우 크게 줄였다

즉:

- 구현은 의도대로 작동했다
- downside lever로서 방향성은 맞다

### 2. 하지만 first pass에서는 same-gate rescue가 아니다

- `Value`, `Quality + Value` 모두
  `Promotion = hold`
  에서 벗어나지 못했다
- 특히 현금 비중이 많이 남으면서
  `CAGR`가 크게 낮아졌다

즉:

- `cash retention only`는
  risk를 줄이는 데는 강하지만
  return drag가 너무 커서
  current practical gate를 회복시키는 레버는 아니었다

### 3. 다음 structural lever 우선순위

이번 결과 기준으로는
다음 우선순위를 이렇게 보는 것이 자연스럽다.

1. `defensive sleeve risk-off`
   - 이유:
     - 현재 문제는 idle cash 비중이 너무 커져서 return drag가 커지는 것이라
       방어 자산 sleeve가 있으면 downside를 줄이면서도 cash drag를 완화할 가능성이 있다
2. `concentration-aware weighting`
   - 이유:
     - overlay 없이도 drawdown을 더 부드럽게 만드는 방향을 같이 볼 수 있다

## 실무 해석

이 문서는
새 candidate를 고정한 report가 아니라,
Phase 17 first structural lever가
실제 strongest/current anchor를 바꾸는 데 충분했는지 확인한
first-pass 결과 문서다.

현재 해석은:

- `Value` current anchor는 그대로 유지
- `Quality + Value` strongest practical point도 그대로 유지
- partial cash retention은
  `MDD reduction lever`
  로는 유효하지만
  `same-gate practical rescue lever`
  로는 아직 부족하다
