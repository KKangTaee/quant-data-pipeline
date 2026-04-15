# Phase 20 Next Phase Preparation

## 이 문서는 무엇인가
- `Phase 20`이 practical closeout된 뒤,
  다음 phase에서 어떤 질문을 이어가면 자연스러운지 정리하는 handoff 문서다.

## 목적
- operator workflow hardening 이후,
  다음 단계가 다시 deep validation인지,
  더 많은 automation인지,
  아니면 portfolio-level 확장인지 판단할 기준을 남긴다.

## 쉽게 말하면
- `Phase 20`은 "후보를 다시 쓰는 흐름"을 정리했다.
- 이제 다음에는
  - 이 흐름을 더 자동화할지
  - 이 흐름 위에서 더 깊게 검증할지
  를 고르면 된다.

## 왜 필요한가
- 좋은 후보가 있어도,
  다시 불러오고 저장하고 이어서 쓰는 흐름이 불안정하면
  deep validation이나 later-phase portfolio work도 비효율적이 된다.
- `Phase 20`이 그 기반을 정리했으니,
  이제는 그 위에 어떤 확장을 올릴지 질문이 더 선명해졌다.

## 이 phase가 끝나면 좋은 점
- 다음 phase가 "막연한 다음 작업"이 아니라,
  이미 정리된 operator workflow 위에서 무엇을 더 할지 선택하는 단계가 된다.

## 현재 기준 handoff 요약

- current candidate는 compare로 다시 보내기 쉬워졌다.
- compare 결과는 weighted portfolio builder에서 source context와 함께 읽을 수 있다.
- saved portfolio는 edit / replay / next step 기준으로 더 직접적으로 읽힌다.
- 즉 연구 후보를 다시 쓰는 기본 operator workflow는 이제 usable한 상태다.

## 다음 phase에서 가장 자연스러운 질문

### 1. deep validation을 다시 열 준비가 되었는가

- operator workflow는 `Phase 20`에서 더 실용적으로 정리됐다.
- `Phase 21` automation baseline도 이미 선행 완료된 상태다.
- 따라서 다음 큰 질문은
  **"이제 current candidate와 saved portfolio 흐름을 바탕으로 더 넓은 rerun / validation을 다시 열 것인가"**
  쪽으로 자연스럽게 이어진다.

### 2. portfolio-level candidate construction을 더 먼저 열 필요가 있는가

- 지금도 weighted portfolio와 saved portfolio는 usable하다.
- 다만 promotion / shortlist / deployment를 portfolio-level candidate까지 어떻게 읽을지에 대한 별도 해석은 아직 더 남아 있다.
- 그래서 다음 phase에서는
  operator workflow를 넘어서
  **portfolio-level candidate semantics**
  를 더 분명히 만들지 검토할 수 있다.

### 3. saved portfolio와 registry를 더 자동화할 필요가 있는가

- current candidate registry와 phase automation baseline은 이미 만들어져 있다.
- 다음에는
  - compare bundle persistence
  - saved portfolio naming / bundle tagging
  - scenario replay shortcut
  같은 자동화를 더 붙일지 검토할 수 있다.

## 추천 해석

- 지금은 `Phase 20`에서 workflow usability를 먼저 닫았고,
  `Phase 21`이 automation baseline을 이미 열어둔 상태다.
- 그래서 그 다음은
  **Phase 22 integrated deep validation**
  을 여는 쪽이 가장 자연스럽다.

쉽게 말하면:

- 이제는 "좋은 후보를 다시 쓰는 길"이 어느 정도 생겼으니,
  그 길 위에서 다시 깊게 검증해볼 차례에 더 가깝다.

## 한 줄 정리

- `Phase 20` 다음의 자연스러운 질문은
  **operator workflow를 더 만드는 것보다, 정리된 workflow 위에서 deep validation을 다시 여는 것**이다.
