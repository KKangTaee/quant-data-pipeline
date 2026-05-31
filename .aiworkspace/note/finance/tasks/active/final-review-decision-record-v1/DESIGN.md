# Final Review Decision Record V1 Design

## Current State

현재 Final Review는 Candidate Board -> Decision Cockpit -> Final Decision Record -> Evidence Appendix 순서로 표시된다. 다만 Final Decision Record 구간은 selectbox와 text area 중심이라, 사용자가 아래 내용을 저장 전에 한눈에 확인하기 어렵다.

- suggested decision과 사용자가 고른 route의 차이
- selected-route gate가 선정 저장을 허용하는지
- operator reason / decision id 같은 필수 기록 조건
- 보류 / 거절 / 재검토 route가 blocker가 있어도 기록 가능한 route라는 점
- live approval / order가 아니라 최종 검토 기록이라는 경계

## Implementation Direction

- `build_final_review_decision_record_guide`를 추가한다.
- 입력은 기존 `decision_route`, `decision_evidence`, `investability_packet`만 사용한다.
- 출력은 Streamlit-free dict로 유지한다.
  - `selected_route_label`
  - `suggested_decision_route`
  - `selected_route_gate`
  - `checklist_rows`
  - `route_templates`
  - `record_boundary`
- UI는 최종 판단 selectbox 선택 후 guide를 렌더링한다.
- 저장 가능 여부의 최종 판단은 기존 `_build_final_review_save_evaluation`을 계속 사용한다.

## Non-Goals

- No new validation calculation.
- No new registry file.
- No JSONL schema expansion.
- No structured waiver UI or persistence.
- No broker approval, order, account sync, or auto rebalance.
