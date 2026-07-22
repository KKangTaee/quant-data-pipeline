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
