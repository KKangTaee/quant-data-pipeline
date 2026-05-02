# Phase 15 Candidate Quality Improvement Plan

## 목적

- Phase 14에서 gate blocker와 calibration 질문을 충분히 좁힌 뒤,
  이제 실제로 더 나은 practical candidate를 만드는 workstream을 연다.
- 이번 phase의 우선순위는
  gate를 더 쉽게 통과시키는 것보다,
  **전략 자체의 candidate quality를 개선하는 것**이다.

## 왜 지금 이 phase가 필요한가

- `Value > Strict Annual`은 strongest current candidate를 확보했지만
  `MDD`가 아직 깊다.
- `Quality`, `Quality + Value`는
  여전히 desired practical candidate 수준에 충분히 못 올라왔다.
- 따라서 다음 질문은
  “어떤 gate를 완화할까?”보다
  **“어떤 조합이 더 나은 전략 품질을 보여주는가?”**가 된다.

## 핵심 workstream

### 1. Value downside-improvement search

- 목표:
  - `Promotion != hold`를 유지하면서
  - `MDD`를 줄일 수 있는 조합을 찾는다.
- 주요 레버:
  - factor subset / controlled factor addition
  - `Trend Filter`
  - `Market Regime`
  - `Top N`
  - `Rebalance Interval`

### 2. Quality candidate-improvement search

- 목표:
  - `Quality` family에서
    `production_candidate` 또는 그 이상에 가까운 practical 후보를 찾는다.
- 주요 레버:
  - controlled factor expansion shortlist
  - defensive overlay 조합
  - cadence / concentration 조정

### 3. Quality + Value candidate-improvement search

- 목표:
  - blended family가
    현재보다 더 나은 practical candidate profile을 만들 수 있는지 확인한다.
- 주요 레버:
  - blend factor subset
  - defensive overlay
  - turnover / consistency tradeoff

### 4. Strategy-specific backtest log accumulation

- 목표:
  - 탐색이 ad hoc로 흩어지지 않게
    전략별 backtest log에 의미 있는 run을 누적한다.
- 산출물:
  - strongest candidate
  - downside-improved near-miss
  - non-hold candidate
  - failed but informative diagnostic run

## 이번 phase에서 당장 하지 않는 것

- blanket real-money gate relaxation
- 새로운 대형 strategy family 추가
- full live automation

이유:

- 지금 더 중요한 것은
  **현재 family에서 더 좋은 후보를 실제로 만드는 것**이기 때문이다.

## 성공 기준

- `Value`에서 strongest baseline보다
  drawdown이 더 낮은 practical candidate 또는 near-miss를 최소 1개 확보
- `Quality`, `Quality + Value`에서
  의미 있는 non-hold candidate를 다시 탐색 / 정리
- 전략별 backtest log 구조 위에
  candidate improvement 탐색 결과를 누적

