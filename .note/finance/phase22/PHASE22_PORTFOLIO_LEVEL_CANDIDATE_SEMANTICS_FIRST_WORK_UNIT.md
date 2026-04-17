# Phase 22 Portfolio-Level Candidate Semantics First Work Unit

## 이 문서는 무엇인가

- 이 문서는 `Phase 22` 첫 번째 작업 단위다.
- 목적은 weighted portfolio를 아무 결과표가 아니라
  **portfolio-level candidate**로 다루기 위한 최소 기준을 정하는 것이다.

## 쉽게 말하면

- `Phase 21`에서는 "전략 3개를 묶어서 저장하고 다시 돌려도 같은 결과가 나오나"를 확인했다.
- `Phase 22`에서는 한 단계 더 나아가
  "그 묶음을 실제 후보라고 부르려면 무엇이 필요하지?"를 정한다.

## 왜 먼저 이걸 하나

- 기준 없이 portfolio 조합부터 많이 돌리면,
  결과는 많아지지만 어떤 조합이 진짜 후보인지 판단하기 어렵다.
- 특히 `Value`, `Quality`, `Quality + Value`는 서로 비슷한 strict annual 계열이므로,
  단순히 섞었다고 자동으로 분산 효과가 충분하다고 볼 수 없다.
- 그래서 먼저 후보 기준을 정하고,
  그 기준에 맞춰 baseline portfolio를 다시 검증하는 순서가 더 안전하다.

## 기본 정의

### Component Strategy

- portfolio 안에 들어가는 각각의 단일 전략이다.
- 예:
  - `Value Strict Annual` current anchor
  - `Quality Strict Annual` current anchor
  - `Quality + Value Strict Annual` current anchor

### Portfolio Bridge

- compare에서 나온 여러 전략 결과를
  weighted portfolio와 saved portfolio replay까지 이어보는 연결 검증이다.
- `Phase 21`의 `33 / 33 / 34` 검증은 portfolio bridge다.
- 즉 "이 흐름이 재현 가능한가"를 확인한 것이지,
  아직 "이 포트폴리오가 최종 후보인가"를 확정한 것은 아니다.

### Portfolio-Level Candidate

- 여러 component strategy를 정해진 weight로 섞고,
  기간, universe, date alignment, source, replay 결과까지 함께 남긴 portfolio 후보다.
- 단순히 화면에서 한 번 만든 weighted portfolio는 후보가 아니다.
- 후보가 되려면 최소한 아래 정보가 남아야 한다.

## Portfolio-Level Candidate 최소 기록 항목

| 항목 | 왜 필요한가 |
|---|---|
| component strategy 목록 | 어떤 전략을 섞었는지 알아야 한다 |
| source document / candidate source | 각 component가 어디서 온 후보인지 추적해야 한다 |
| validation period | 어떤 기간에서 본 결과인지 고정해야 한다 |
| universe frame | 서로 다른 universe 결과를 섞지 않기 위해 필요하다 |
| weight | portfolio 결과의 핵심 입력이다 |
| date alignment | 여러 전략의 날짜를 어떻게 맞췄는지 알아야 한다 |
| benchmark / guardrail interpretation | 단일 전략과 portfolio-level 비교 해석이 달라질 수 있다 |
| key metrics | `CAGR`, `MDD`, `Sharpe`, `End Balance` 등 결과 요약이다 |
| saved replay result | 저장 후 다시 실행해도 같은 결과가 나오는지 확인한다 |
| interpretation / next action | 유지, 교체, 보류 중 무엇인지 판단을 남긴다 |

## 후보 판단 규칙 초안

### 유지

- portfolio 결과가 단일 component보다 무조건 좋아야만 유지되는 것은 아니다.
- 대신 아래 조건을 만족하면 유지 후보로 볼 수 있다.
  - 재현 가능한 saved replay가 있다.
  - component strategy들이 current anchor 또는 명확한 후보 상태다.
  - `CAGR / MDD / Sharpe`가 단일 전략 대비 합리적인 tradeoff를 만든다.
  - report에서 왜 이 조합을 계속 볼지 설명되어 있다.

### 교체

- 기존 portfolio baseline을 다른 조합으로 교체하려면 더 강한 근거가 필요하다.
  - 같은 validation frame에서 비교됐다.
  - MDD나 Sharpe가 개선됐고, CAGR 손상이 크지 않다.
  - component status가 더 약해지지 않는다.
  - saved replay가 exact match 또는 허용 가능한 범위로 재현된다.

### 보류

- 아래 상황이면 좋은 숫자가 있어도 보류한다.
  - component 중 일부가 comparison-only 또는 weaker-gate다.
  - date alignment 때문에 비교 기간이 크게 달라졌다.
  - saved replay가 재현되지 않는다.
  - 결과는 좋지만 왜 좋은지 설명이 부족하다.
  - 같은 family 성격이 너무 강해서 실질 분산 효과가 불명확하다.

## Phase 21 결과의 현재 해석

- `33 / 33 / 34` portfolio bridge 결과:
  - `CAGR = 28.66%`
  - `MDD = -25.42%`
  - `Sharpe = 1.51`
  - saved replay exact match
- 현재 해석:
  - workflow 재현성은 확인됐다.
  - baseline portfolio candidate로 다시 볼 가치는 있다.
  - 하지만 최종 portfolio winner로 확정되지는 않았다.
  - component들이 모두 strict annual 계열이라 분산 효과 검증은 아직 부족하다.

## 이번 작업의 결정

- `Phase 22`에서는 먼저 `33 / 33 / 34` bridge를
  **baseline portfolio candidate pack의 출발점**으로 둔다.
- 단, 이 조합을 최종 후보로 승격하지 않고,
  아래 질문을 검증할 기준점으로만 사용한다.
  - 같은 component로 weight를 바꾸면 tradeoff가 좋아지는가
  - annual strict family끼리만 묶는 것이 충분히 의미 있는가
  - future phase에서 quarterly나 new strategy를 추가할 때 비교 기준으로 쓸 수 있는가

## 다음 작업

- 다음 작업은 `Representative Portfolio Candidate Pack`을 구성하는 것이다.
- 우선 검토할 후보:
  - `33 / 33 / 34` near-equal baseline
  - `1 / 1 / 1` pure equal-weight equivalent
  - drawdown-aware alternative weight, 단 이번 phase 범위 안에서 과도한 탐색은 피한다

## 한 줄 정리

- portfolio-level candidate는 "전략을 섞은 결과표"가 아니라,
  source, weight, date alignment, replay, 해석이 함께 남은 재현 가능한 후보 기록이다.
