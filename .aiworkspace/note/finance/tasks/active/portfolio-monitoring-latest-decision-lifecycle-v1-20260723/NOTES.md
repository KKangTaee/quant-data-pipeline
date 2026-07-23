# Portfolio Monitoring Latest Decision Lifecycle V1 Notes

## Diagnosis

- `load_current_final_selection_decisions`는 append-only row를 시간순으로 읽지만 subject별 최신 상태를 만들지 않는다.
- 신규 Monitoring catalog와 Selected Strategy adapter는 개별 row의 `monitoring_candidate is True`만 검사한다.
- 동일 subject의 최신 non-select 판단이 있어도 과거 selected row는 계속 신규 목록과 기존 replay에서 유효하다.

## Decisions

- canonical subject key는 `selection_source_id -> source_type/source_id -> decision_id` 순서다.
- 기존 item은 삭제하지 않는다.
- 최신 non-select 판단은 item-local replay blocker다.
- 계속 추적하려면 Final Review가 새 selected 판단을 소유한다.
- 종료는 기존 Portfolio Monitoring `end_item` 명령이 소유한다.
- 동일 timestamp fallback은 loader 입력 순서가 아니라 `updated_at -> created_at -> decision_id`로 결정해 실행마다 같은 latest row를 선택한다.
- 기존 item의 과거 decision ID는 requested provenance로 남기고 최신 selected decision ID를 effective provenance로 사용한다.

## Implementation

- `decision_lifecycle.py`가 `DECISION_NOT_FOUND`, `CURRENT_SELECTED`, `SUPERSEDED_SELECTED`, `TRACKING_ELIGIBILITY_CHANGED`를 한 곳에서 계산한다.
- catalog는 subject별 최신 row 중 strict `monitoring_candidate is True`만 노출한다.
- selected-strategy adapter는 registry를 한 번 읽고 기존 requested decision의 subject를 해석한다. 최신 selected면 effective row로 replay하고 최신 non-select면 item-local readiness blocker를 반환한다.
- read model은 성공 lane과 readiness exception 모두에서 lifecycle projection을 item row에 보존해 그룹 전체 실패로 확산하지 않는다.
- React는 lifecycle을 재계산하지 않고 잠금 카드, 최신 route, `최신 판단 재확인`만 표시한다. 잠금 중에는 새 결과 차트를 표시하지 않는다.
- Final Review 이동은 `monitoring_item_id`만 client event로 받고, Python이 item/source/lifecycle을 다시 검증해 latest source hint를 정한다.
