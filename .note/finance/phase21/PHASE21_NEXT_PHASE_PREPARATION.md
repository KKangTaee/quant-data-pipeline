# Phase 21 Next Phase Preparation

## 목적

- Phase 21 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리한다.

## 현재 handoff 상태

- phase 문서 묶음을 자동 생성하는 baseline이 생겼다.
- current candidate를 machine-readable registry로 남길 수 있게 됐다.
- plugin / skill / hygiene 흐름도 새 automation baseline을 알게 됐다.

즉 이제는:
- phase를 여는 반복 작업
- current candidate를 다시 참조하는 반복 작업

이전보다 덜 수동으로 해도 되는 상태가 됐다.

## 다음 phase에서 더 중요한 질문

### 1. operator workflow를 실제 UI에서 더 짧게 만들 것인가

- current candidate registry는 생겼지만,
  실제 compare / weighted / saved portfolio re-entry UX는 아직 `Phase 20`의 메인 질문으로 남아 있다.

### 2. scenario persistence를 current candidate 밖으로 더 넓힐 것인가

- 지금은 current candidate 중심 registry를 먼저 열었다.
- 다음에는:
  - compare bundle
  - weighted portfolio scenario
  - saved portfolio bridge
  까지 같은 persistence layer로 넓힐지 판단할 수 있다.

## 추천 다음 방향

### 추천 1. `Phase 20` operator workflow hardening 재집중

- 이유:
  - `Phase 21`에서 automation baseline은 생겼고,
    이제 그 자동화가 실제로 도움 되는 UI/operator 동선 쪽을 다시 밀어주는 것이 자연스럽다.

### 추천 2. 그 다음 `Phase 22` deep validation 준비

- 이유:
  - 현재는 candidate persistence와 phase 문서 automation이 더 좋아졌기 때문에,
    deep rerun을 다시 열 때도 정리 비용이 줄어든다.

## handoff 메모

- 다음 phase에서 candidate-facing 문서가 바뀌면
  `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`도 같이 보는 것이 좋다.
- 다음 phase kickoff에는
  `bootstrap_finance_phase_bundle.py`를 먼저 쓰는 것이 자연스럽다.
