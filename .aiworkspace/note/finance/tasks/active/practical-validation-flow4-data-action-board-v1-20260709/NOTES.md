# Notes

## Context Findings

- `단계별 검증 소유권`은 내부 inventory로 유용하지만 Final Review / Monitoring 소유 항목까지 사용자-facing Flow 4에 보여 단계 경계를 흐릴 수 있다.
- 기존 `수집 대상 근거`는 Provider / Data 보강 액션과 분리된 Streamlit expander라 사용자가 바로 수집 가능한 항목을 먼저 읽기 어렵다.
- `근거 부록`은 검산용으로 필요하므로 삭제하지 않고 보조 상세 영역으로 낮춘다.

## Boundary Decision

- React는 표시 전용이다.
- Python service가 수집 계획, ingestion job orchestration, replay, gate, registry / saved write 경계를 유지한다.

## QA Finding

- Browser QA 중 `Final Review Readiness Preview`가 처음에는 `no_action` 카드로 보였다.
- 이는 Final Review 판단 항목을 PV 메인 UI에 반복 노출하지 않는 원칙과 맞지 않아, `selected_route_preflight` module id뿐 아니라 Final Review / Monitoring label-group token도 `data_action_board`에서 제외하도록 보정했다.
