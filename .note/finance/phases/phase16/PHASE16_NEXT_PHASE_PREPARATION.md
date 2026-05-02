# Phase 16 Next Phase Preparation

## 목적

- Phase 16 이후 다음 phase를 어떤 방향으로 여는 것이 가장 합리적인지 정리한다.
- 지금까지 확인한 strongest practical point와 lower-MDD near-miss를
  다음 workstream 질문으로 연결한다.

## 현재 handoff 상태

Phase 16을 통해 아래는 확실히 고정되었다.

- `Value`
  - current best practical point:
    - `Top N = 14 + psr`
    - `28.13% / -24.55%`
  - strongest lower-MDD near-miss:
    - `Top N = 14 + psr + pfcr`
    - `27.22% / -21.16%`
    - but `production_candidate / watchlist`
- `Quality + Value`
  - current strongest practical point:
    - `operating_margin + pcr + por + per`
    - `Top N = 10`
    - `31.82% / -26.63%`
    - `real_money_candidate / small_capital_trial`
  - lower-MDD near-miss:
    - `Top N = 9`
    - `32.21% / -25.61%`
    - but `production_candidate / watchlist`

즉 지금은
“bounded tweak으로 더 좋아질 수 있나”보다
**구조를 바꾸면 lower-MDD practical candidate를 만들 수 있나**
를 묻는 단계다.

## 다음 phase에서 더 중요한 질문

### 1. structural downside improvement

- `Value`의 `+ pfcr` near-miss를
  왜 `production_candidate / watchlist`에서 멈추는지
  구조적으로 개선할 수 있는가
- `Quality + Value`의 `Top N = 9` 또는 `cash_ratio` 대안을
  same gate로 rescue할 수 있는 구조 레버가 있는가

### 2. candidate consolidation

- strongest practical point와 lower-MDD near-miss를
  operator 관점에서 어떻게 함께 관리할 것인가
- family별 후보를 saved portfolio / compare / shortlist로
  어떻게 묶을 것인가

### 3. operator workflow persistence

- current strongest candidate를
  operator note / shortlist / saved portfolio와
  어떻게 연결할 것인가

## 추천 다음 방향

### 추천 1. Structural Downside Improvement Phase

우선순위:

- `Value`
  - lower-MDD near-miss rescue
  - weighting / selection / defensive structure 실험
- `Quality + Value`
  - stronger gate를 유지하는 lower-MDD 구조 실험
  - benchmark / quality sleeve / concentration 구조 실험

이 방향이 좋은 이유:

- 지금 핵심 목표가
  **낮은 `MDD`, 높은 수익률, 그리고 실전 사용 가능 전략**
  이기 때문이다
- bounded tweak은 이미 많이 봤고,
  이제는 구조를 건드려야 실제 개선이 나올 가능성이 높다

### 추천 2. Candidate Consolidation Phase

우선순위:

- current strongest / near-miss candidate summary cards
- family 간 comparison surface
- shortlist / saved portfolio linkage

이 방향이 좋은 이유:

- 이미 후보는 충분히 생겼고,
  이제는 그 후보를 operator 관점에서 정리할 가치가 있다

## 지금 바로 하지 않는 것

- blanket gate relaxation
- 큰 폭의 factor expansion
- 새로운 대형 전략 family 추가

이유:

- 지금 더 중요한 것은
  문턱을 낮추는 게 아니라
  **전략 구조 자체를 더 좋아지게 만드는 것**
  이기 때문이다

## handoff 메모

- Phase 16 이후 자연스러운 다음 phase는
  **structural downside improvement**다
- candidate consolidation은 그 다음 또는 병행 보조 트랙으로 두는 편이 맞다
