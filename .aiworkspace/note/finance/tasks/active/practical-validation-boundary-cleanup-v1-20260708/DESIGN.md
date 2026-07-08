# Design

## Decision

Practical Validation은 `통과`, `보강 후 재검증`, `실전 사용 어려움`을 중심으로 보여준다.

`REVIEW`는 Final Review의 최종 해석 대상이므로 Flow 3 / Flow 4의 actionable issue나 확인 필요 count로 노출하지 않는다.

## UI Boundary

- Flow 3: Practical Validation 검증 결론과 실패 category count만 보여준다.
- Flow 4: Practical Validation에서 보강해야 할 기준, 원인, 해결 방법만 보여준다.
- Final Review: 선택 / 보류 / 탈락 판단과 `REVIEW` 항목 해석을 담당한다.

## Implementation Notes

- Flow 3 React component no longer renders Final Review move state or review count.
- Flow 4 criteria board no longer renders Final Review reference or move summary blocks.
- Flow 4 technical gate expander was removed from the visible Flow 4 path.
