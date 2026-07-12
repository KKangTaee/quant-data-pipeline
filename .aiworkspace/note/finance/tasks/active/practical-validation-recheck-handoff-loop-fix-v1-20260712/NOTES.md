# Notes

## 2026-07-12 Root Cause

- Final Review recovery handoff 수집 경로는 collection 후 `_clear_practical_validation_replay_state(...)`를 호출하지 않는다.
- 사용자가 collection 뒤 새 validation을 저장하지 않고 Level3로 이동하면 append-only registry의 기존 legacy validation을 다시 연다.
- 조사 시점에 GRS Macro Top3 MA200 source에는 2026-07-11 생성 legacy validation 1개만 저장되어 있었고 새 validation row는 없었다.

## 2026-07-12 Latest Validation Rule

- append-only validation history는 보존하지만 Final Review current 후보는 `selection_source_id`별 최신 row만 사용한다.
- eligibility filtering은 latest selection 뒤에 적용한다. 최신 row가 blocked면 과거 eligible row를 대신 표시하지 않는다.
- 명시적인 save-and-move는 새 validation stable key를 selector와 confirmed state에 함께 전달하므로 별도 후보 재선택 없이 새 검토서를 연다.

## 2026-07-12 User Completion Sequence

- 자료 보강 성공은 validation 성공이 아니다. 성공 직후 current replay state를 지우고 `Flow 2 재검증 필요`로 전환한다.
- Final Review 이동은 current-session replay가 존재하고 새 validation row 저장이 끝난 뒤에만 허용한다.
- Final Review는 source별 최신 validation만 current 후보로 사용한다. 최신 row가 Gate 미통과면 과거 통과 row로 되돌아가지 않는다.
- `저장하고 Final Review로 이동`은 새 `practical_validation_result:<validation_id>`를 선택·확정하므로 사용자가 구형 검토서를 다시 열지 않는다.

## 2026-07-12 Browser QA Note

- in-app Browser에서 Final Review의 재검증 필요 상태, 판단 CTA 비활성, REVIEW 근거, 760px outer / iframe no-overflow를 확인했다.
- custom component의 `setComponentValue` navigation intent는 in-app Browser 자동화에서 Streamlit rerun으로 관측되지 않아 실제 provider 수집 없는 전체 클릭 체인은 재현하지 않았다. Python intent consumer와 recovery progress / save guard / latest-row handoff는 focused contract tests로 검증했다.
