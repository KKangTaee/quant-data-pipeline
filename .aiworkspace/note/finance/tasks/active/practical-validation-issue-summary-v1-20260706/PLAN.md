# Practical Validation Issue Summary V1 Plan

## 이걸 하는 이유?

직전 Flow 3 / Flow 4 개선은 raw audit 용어를 줄였지만, 카드가 `무엇을 검증했나 / 부족한 점 / 해야 할 일` 같은 가이드형 문단으로 보여 사용자가 실제로 무엇을 수정해야 하는지 바로 읽기 어렵다.
이번 작업은 같은 gate evidence를 유지하면서 Flow 3는 실제 이슈 큐, Flow 4는 기준별 통과 / 보강 요약표로 다시 정리한다.

## Scope

- Flow 3 `먼저 해결할 일`을 `Final Review 이동을 막는 이슈` 중심으로 바꾼다.
- 각 이슈는 `현재 문제 / 완료 기준 / 보강 위치`로 보여준다.
- Flow 4 `Final Review로 넘기기 전 확인 기준`은 `상태 / 통과한 기준 / 남은 문제 / 판정` 요약을 먼저 보여준다.
- `NEEDS_INPUT`, `NOT_RUN`, `REVIEW` 같은 raw status는 기술 tag로 유지하되 first-read label로 쓰지 않는다.
- Gate threshold, replay execution, provider collection, registry / saved JSONL, Final Review persistence는 변경하지 않는다.

## Steps

1. RED tests for issue-card fields and criteria-summary board copy.
2. Add issue-focused fields and group summary fields to the workspace read model.
3. Update Flow 3 React component to remove guide labels and render issue cards.
4. Update Flow 4 board to render criteria summary cards before raw evidence detail.
5. Rebuild, run focused tests, Browser QA, docs sync, commit.
