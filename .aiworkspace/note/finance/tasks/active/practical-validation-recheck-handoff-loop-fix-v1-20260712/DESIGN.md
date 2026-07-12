# Design

## 이걸 하는 이유?

Final Review의 legacy 검토서에서 Practical Validation 데이터 보강으로 이동한 사용자가 수집만 실행하고 Level3로 돌아오면, 새 validation이 저장되지 않았기 때문에 같은 과거 검토서를 다시 열게 된다. 현재 Final Review handoff 전용 수집 경로는 일반 Flow 4 수집 경로와 달리 replay state를 초기화하지 않아 `수집 완료`와 `재검증 완료` 경계도 화면에서 흐려진다.

## Approved Goal

`데이터 보강 -> Flow 2 재검증 -> 새 validation 저장 -> 새 Final Review 검토서` 순서를 강제하고, 같은 후보의 구형 검토서는 새 결과가 생긴 뒤 기본 후보 목록에서 제외한다.

## Considered Approaches

1. 안내 문구만 추가: 구현은 작지만 stale replay와 기존 validation 재선택을 막지 못하므로 제외한다.
2. 기존 Streamlit session state와 Python Gate를 하나의 완료 순서로 통합: 새 저장소 없이 현재 경계를 지키면서 반복을 차단할 수 있어 채택한다.
3. 별도 persistent workflow-state registry 추가: 추적성은 높지만 이번 문제에 비해 과하며 JSONL source-of-truth를 늘리므로 제외한다.

## Design

### Collection Completion Boundary

- 일반 Flow 4 수집과 Final Review handoff 수집은 같은 Python completion helper를 사용한다.
- completion helper는 collection result를 session에 남기고 해당 source의 replay output을 항상 제거한다.
- collection success alone은 validation success가 아니다. replay가 다시 실행되기 전에는 Flow 3 / Flow 4와 save-and-move action을 렌더링하지 않는다.

### Level2 Progress

- Final Review recovery로 들어온 후보에는 `자료 보강`, `Flow 2 재검증`, `새 결과 저장`, `Final Review 확인`의 4단계 상태를 표시한다.
- 수집 직후에는 Flow 2를 다음 행동으로 강조한다.
- 재검증 후 Gate가 통과하면 저장 단계만 활성화하고, 여전히 blocking이면 Flow 4 해결 항목을 유지한다.
- 별도 job/status 진단 패널을 만들지 않고 사용자가 완료해야 할 순서만 first-read에 표시한다.

### Save And Final Review Handoff

- `저장하고 Final Review로 이동`은 현재 session replay가 존재하고 Gate가 통과할 때만 실행된다.
- 저장 성공 후 새 validation stable key를 Final Review selector와 confirmed state에 함께 전달한다. 이 명시적 save-and-move action 자체를 새 검토서 확인으로 간주한다.

### Latest Validation Selection

- Practical Validation registry는 append-only로 보존한다.
- Final Review 기본 후보 목록은 `selection_source_id`별 최신 validation만 소비한다.
- 최신 row가 blocking이면 같은 source의 과거 eligible row로 fallback하지 않는다.
- 새 current row가 생기기 전에는 기존 legacy row를 recovery entry로 유지한다.

## Error Handling

- collection job 일부가 실패해도 replay는 초기화한다. 사용자는 Flow 2 재검증 후 현재 DB evidence 기준 Gate를 다시 확인한다.
- 재검증 후 blocker가 남으면 save-and-move는 비활성화하고 기록용 저장만 허용한다.
- source id 또는 validation id가 없으면 자동 선택을 만들지 않고 기존 안전한 selector 흐름으로 fallback한다.

## Boundaries

- React는 새 실행, collection, Gate, 저장을 수행하지 않는다.
- provider fetch는 Practical Validation Python action에서만 실행한다.
- Final Review는 live approval, broker order, account sync, auto rebalance가 아니다.
- registry / saved JSONL 기존 row를 재작성하거나 삭제하지 않는다.
- run history와 QA screenshot은 generated artifact로 commit하지 않는다.

## Verification

- handoff collection과 regular collection 모두 replay state를 초기화하는 contract test
- replay 전 save-and-move 차단 test
- save 성공 후 new validation stable key 전달 test
- source별 latest row selection과 blocked-latest fallback 방지 test
- Browser QA로 실제 반복 경로와 compact viewport 확인
