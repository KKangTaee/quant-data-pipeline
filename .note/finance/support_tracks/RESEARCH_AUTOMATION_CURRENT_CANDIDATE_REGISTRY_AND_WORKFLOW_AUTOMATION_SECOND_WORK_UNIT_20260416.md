# Phase 21 Current Candidate Registry And Workflow Automation Second Work Unit

## 목적
- current candidate를 machine-readable registry로 남기고,
  기존 hygiene workflow도 그 registry를 인식하게 만든다.

## 쉽게 말하면
- 이제 current candidate는 사람용 문서만 있는 것이 아니라,
  script와 plugin도 다시 읽을 수 있는 JSONL 기록으로도 남는다.

## 이번 작업에서 한 것
- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`를 만들었다.
- `plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py`를 추가했다.
- 이 script는 아래 기능을 제공한다.
  - `seed-current-practical`
  - `list`
  - `show`
  - `append`
  - `validate`
- `check_finance_refinement_hygiene.py`도 보강해
  current candidate 관련 문서가 바뀔 때 registry도 같이 확인할 수 있게 했다.

## 왜 이 작업이 필요한가
- current candidate summary는 좋은 사람용 문서지만,
  automation은 Markdown만으로는 이어붙이기 어렵다.
- registry가 있으면:
  - plugin이 현재 strongest candidate를 다시 읽을 수 있고
  - future scenario persistence와도 더 잘 연결되고
  - candidate management가 문서+script 두 층으로 정리된다.

## 현재 seed된 후보
- `Value` current anchor
- `Value` lower-MDD near-miss
- `Quality` current anchor
- `Quality` cleaner alternative
- `Quality + Value` strongest practical point
- `Quality + Value` lower-MDD near-miss

## 기대 효과
- candidate management가 더 재현 가능해진다.
- future automation이 `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`만 읽는 구조에서 벗어난다.
- plugin workflow가 current candidate를 더 직접적으로 다시 참조할 수 있다.

## 한 줄 정리
- 두 번째 작업은 **current candidate를 문서뿐 아니라 registry에도 남겨, automation이 다시 쓸 수 있는 persistence layer를 여는 것**이다.
