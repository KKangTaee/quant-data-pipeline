# Phase 18 Next Phase Preparation

## 목적

- `Phase 18` 이후 다음 main phase를 어떤 기준으로 여는 것이 자연스러운지 정리한다.
- remaining structural backlog를 지금 당장 더 구현할지,
  아니면 integrated validation으로 넘어갈지 판단 근거를 남긴다.

## 현재 handoff 상태

`Phase 18`을 통해 아래는 확실히 정리되었다.

- larger structural redesign이라는 질문은 실제 코드로 열렸다
- first slice인 `next-ranked eligible fill`은
  meaningful redesign evidence로 남았다
- 하지만 current practical anchor replacement나
  same-gate lower-MDD rescue까지는 아니었다
- `Phase 19`, `Phase 20`에서
  contract language와 operator workflow도 practical 수준으로 정리되었다

즉 지금은
"구조 실험을 하나 더 붙여볼까"보다
**지금까지 만든 current candidate와 bridge를 같은 frame에서 다시 검증할 때**
가 더 적절하다.

## 지금 더 중요한 질문

### 1. annual strict current anchor를 같은 frame에서 다시 검증할 것인가

- `Value`
- `Quality`
- `Quality + Value`

의 current anchor / lower-MDD alternative / near-miss를
이제 같은 frame에서 다시 보고,
유지 / 교체 / 보류 판단을 더 분명하게 해야 한다.

### 2. portfolio bridge가 실제 candidate lane인지 확인할 것인가

- `compare -> weighted -> saved` workflow는
  `Phase 20`에서 실사용 흐름으로 정리되었다.
- 이제 필요한 것은
  이 bridge가 단순 operator artifact인지,
  아니면 다음 phase에서 portfolio-level candidate로 볼 수 있는 lane인지 판단하는 일이다.

### 3. second-slice structural backlog를 지금 다시 열 것인가

- current 판단으로는
  second-slice 아이디어는 immediate blocker가 아니다.
- integrated validation 결과 없이 second slice를 더 열면,
  또 다른 redesign evidence만 늘고
  현재 anchor 유지 / 교체 판단은 여전히 흐려질 수 있다.

## 추천 다음 방향

### 추천 1. `Phase 21` Integrated Deep Backtest Validation

우선순위:

- annual strict family current anchor / alternative rerun
- representative portfolio bridge validation
- strategy hub / backtest log / current candidate summary refresh

왜 추천하나:

- 지금은 구조 실험을 더 붙이는 것보다,
  이미 만든 후보를 한 frame에서 다시 읽는 편이 더 중요하기 때문이다.

### 추천 2. remaining structural backlog는 future option으로 유지

우선순위:

- second-slice shortlist
- larger redesign follow-up
- deeper rerun expansion

왜 지금 바로 하지 않나:

- 이것들은 `Phase 21` 결과 이후에도 늦지 않다
- 반면 `Phase 21`을 미루면,
  current candidate 판단이 계속 phase별 증거에만 나뉘어 남게 된다

## 지금 바로 하지 않는 것

- `Phase 18` second slice 실제 구현
- broader deep rerun 재개
- new strategy expansion

이유:

- 지금 더 중요한 것은
  **새 구조를 하나 더 여는 것보다, 지금까지 만든 strongest candidate를 다시 검증하는 것**
  이기 때문이다.

## handoff 메모

- `Phase 18` 이후 가장 자연스러운 다음 main phase는
  **`Phase 21` Integrated Deep Backtest Validation**
  이다
- remaining structural backlog는 버리는 것이 아니라
  future structural option으로 남겨둔다
- 따라서 다음 흐름은
  - `Phase 18` closeout
  - `Phase 21` validation kickoff
  - 이후 결과에 따라 `Phase 22 ~ 25`
  로 읽는 것이 가장 자연스럽다
