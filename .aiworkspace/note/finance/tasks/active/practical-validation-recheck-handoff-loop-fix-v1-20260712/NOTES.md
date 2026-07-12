# Notes

## 2026-07-12 Root Cause

- Final Review recovery handoff 수집 경로는 collection 후 `_clear_practical_validation_replay_state(...)`를 호출하지 않는다.
- 사용자가 collection 뒤 새 validation을 저장하지 않고 Level3로 이동하면 append-only registry의 기존 legacy validation을 다시 연다.
- 조사 시점에 GRS Macro Top3 MA200 source에는 2026-07-11 생성 legacy validation 1개만 저장되어 있었고 새 validation row는 없었다.

## 2026-07-12 Latest Validation Rule

- append-only validation history는 보존하지만 Final Review current 후보는 `selection_source_id`별 최신 row만 사용한다.
- eligibility filtering은 latest selection 뒤에 적용한다. 최신 row가 blocked면 과거 eligible row를 대신 표시하지 않는다.
- 명시적인 save-and-move는 새 validation stable key를 selector와 confirmed state에 함께 전달하므로 별도 후보 재선택 없이 새 검토서를 연다.
