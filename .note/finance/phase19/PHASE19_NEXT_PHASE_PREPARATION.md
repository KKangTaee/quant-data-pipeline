# Phase 19 Next Phase Preparation

## 목적

- Phase 19 이후 다음 phase를 어떤 성격으로 여는 것이 자연스러운지 정리한다.
- 이번 phase에서 정리한 usable contract를
  다음 workstream 질문으로 연결한다.

## 현재 handoff 상태

Phase 19를 통해 아래는 확실히 고정되었다.

- strict annual 구조 옵션은 이제 이전보다 훨씬 읽기 쉬운 contract 언어를 가진다.
  - rejected-slot handling
  - weighting
  - risk-off
- single / compare / history / prefill / interpretation이
  같은 contract 언어를 쓰도록 많이 정리됐다.
- deep backtest를 다시 크게 열기 전에 필요한
  "해석 정렬" 작업은 practical 수준으로 마무리됐다.

즉 지금은
"이 옵션이 무슨 뜻인지"를 먼저 풀어야 하는 단계가 아니라,
**정리된 contract를 바탕으로 다음 연구/운영 흐름을 여는 단계**
라고 보는 게 맞다.

## 다음 phase에서 더 중요한 질문

### 1. candidate consolidation / operator workflow를 먼저 강화할 것인가

- 지금 strongest / near-miss candidate는 이미 문서화되어 있다.
- 하지만 compare -> weighted -> saved portfolio 흐름은
  operator workflow 관점에서 더 다듬을 여지가 있다.

즉 다음 질문은:

- 좋은 후보를 다시 꺼내 보고
- 비교하고
- 저장하고
- 실무적으로 관리하는 흐름을
  더 자연스럽게 연결할 것인가

### 2. research automation / experiment persistence를 바로 당길 것인가

- 지금은 refinement hygiene script, plugin draft, skill draft 같은 기반은 있다.
- 다음 phase에서 이걸 더 practical workflow로 끌어올리면
  반복 연구 비용을 더 줄일 수 있다.

즉 다음 질문은:

- operator workflow를 먼저 단단히 할지
- automation/persistence를 더 먼저 붙일지

를 다시 고르면 된다.

## 추천 다음 방향

### 추천 1. Phase 20 성격의 candidate consolidation / operator workflow hardening

우선순위:

- current strongest / near-miss candidate summary 정리
- compare -> weighted -> saved portfolio bridge polish
- operator가 후보를 다시 보고 저장하는 흐름 개선

왜 추천하나:

- Phase 19에서 "읽는 언어"를 정리했으니,
  다음은 그 후보를 실제로 "관리하는 흐름"을 정리하는 게 자연스럽기 때문이다.

### 추천 2. 그 다음 research automation / experiment persistence

우선순위:

- 반복 rerun / 문서화 / hygiene 체크 자동화
- plugin / skill workflow practical hardening

왜 이 순서가 좋나:

- operator workflow가 먼저 어느 정도 정리돼야
  automation도 무엇을 자동화할지 더 분명해지기 때문이다.

## 지금 바로 하지 않는 것

- deep integrated rerun 재개
- 새 major strategy family 대규모 확장
- quarterly production-readiness 본격 승격

이유:

- 지금 더 중요한 것은
  새 contract를 충분히 읽고 관리할 수 있는 흐름을 먼저 정리하는 것이기 때문이다.

## handoff 메모

- Phase 19 이후 가장 자연스러운 다음 phase는
  **candidate consolidation / operator workflow hardening**
  으로 읽힌다.
- 다만 `AGENTS.md` 기준으로
  새 major phase 방향은 사용자와 다시 확인한 뒤 여는 것이 맞다.
