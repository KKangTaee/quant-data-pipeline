# Service Contract Tests Design

## Test Shape

현재 `.venv`에는 `pytest`가 없으므로 새 검증은 표준 라이브러리 `unittest`로 작성한다.
테스트 파일은 `tests/test_service_contracts.py` 하나로 시작해 service boundary의 public function contract만 확인한다.

## Contract Boundaries

Practical Validation service:

- `prepare_practical_validation_source_handoff(..., persist=False)`는 registry append 없이 UI-neutral handoff dataclass를 반환한다.
- `prepare_practical_validation_source_handoff(..., persist=True)`는 append 함수를 호출하고 `persisted=True`를 반환한다.
- `prepare_final_review_handoff_from_validation(..., persist_validation=False)`는 source/result payload copy를 session payload로 묶고 저장하지 않는다.
- `prepare_final_review_handoff_from_validation(..., persist_validation=True)`는 validation 저장 함수를 호출하고 `persisted=True`를 반환한다.

Evidence read model service:

- saved final decision row의 `decision_route`를 current Final Review status route로 변환한다.
- legacy `phase35_handoff.handoff_route`는 fallback으로 유지한다.
- saved decision table row는 UI가 기대하는 핵심 column을 유지한다.
- final evidence rows는 Final Review / Validation / Robustness / Paper Observation area로 확장된다.

Import boundary:

- fresh Python process에서 service module만 import했을 때 `streamlit` module이 로드되지 않아야 한다.

## Tradeoff

이 테스트는 실제 DB-backed replay나 provider snapshot 검증을 하지 않는다.
대신 UI가 service 반환값에 기대는 최소 contract를 빠르게 잡아, 이후 engine / repository 분리를 진행할 때 회귀를 먼저 감지하게 한다.
