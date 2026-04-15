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

### 1. automation baseline을 deep validation과 later-phase persistence에 어떻게 연결할 것인가

- `Phase 20`에서 compare / weighted / saved portfolio re-entry UX는 manual checklist 기준으로 닫혔다.
- 그래서 이제 더 중요한 질문은,
  current candidate registry와 phase bundle automation을
  later-phase deep validation, scenario persistence, documentation sync에
  어떻게 더 직접적으로 연결할 것인가 쪽이다.

### 2. scenario persistence를 current candidate 밖으로 더 넓힐 것인가

- 지금은 current candidate 중심 registry를 먼저 열었다.
- 다음에는:
  - compare bundle
  - weighted portfolio scenario
  - saved portfolio bridge
  까지 같은 persistence layer로 넓힐지 판단할 수 있다.

## 추천 다음 방향

### 추천 1. `Phase 22` integrated deep validation 준비

- 이유:
  - `Phase 20` operator workflow는 이미 usable + manually validated 상태다.
  - `Phase 21`에서 automation baseline도 생겼으니,
    이제는 그 기반 위에서 deep rerun / validation을 다시 여는 쪽이 더 자연스럽다.

### 추천 2. 그 다음 scenario persistence 확장 검토

- 이유:
  - current candidate registry baseline은 생겼지만,
    compare bundle / weighted scenario / saved portfolio bridge까지 같은 persistence layer로 넓힐 여지는 아직 남아 있다.
  - 다만 이건 deep validation보다 한 단계 뒤의 확장 질문으로 보는 편이 더 자연스럽다.

## handoff 메모

- 다음 phase에서 candidate-facing 문서가 바뀌면
  `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`도 같이 보는 것이 좋다.
- 다음 phase kickoff에는
  `bootstrap_finance_phase_bundle.py`를 먼저 쓰는 것이 자연스럽다.
