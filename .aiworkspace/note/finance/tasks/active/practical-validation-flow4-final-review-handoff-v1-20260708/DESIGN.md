# Design

## Decision

Practical Validation Flow 4는 "지금 보강해야 하는 문제"를 우선 표시한다. REVIEW 항목은 이 화면에서 해결해야 할 검증 실패로 보이지 않게 하고, Final Review에서 해석할 참고 항목 수만 handoff summary로 남긴다.

## Model Contract

- `criteria_review_count`는 기존 호환용으로 유지한다.
- `final_review_reference_count`를 추가해 Flow 4 UI가 REVIEW 항목을 별도 handoff로 읽게 한다.
- 그룹별 `final_review_reference_count`와 `final_review_reference_criteria`를 유지하되, main board는 `remaining_issues`에 REVIEW 항목을 넣지 않는다.
- 전체 outcome은 `BLOCKED`가 있으면 `실전 사용 어려움`, `NEEDS_INPUT / NOT_RUN`이 있으면 `보강 후 재검증 필요`, 그 외에는 `통과`로 읽는다. REVIEW만 남은 상태는 Practical Validation 관점에서 통과다.

## UI Contract

- Flow 4 metric row에서 `Final Review 판단`을 제거한다.
- 그룹 카드의 `Final Review 판단` 컬럼을 제거한다.
- REVIEW 카드 상세는 Flow 4 technical detail에서 렌더링하지 않는다.
- `Final Review 참고` section은 개수와 책임 경계만 알려주고 항목별 판단은 Final Review 화면에 맡긴다.
