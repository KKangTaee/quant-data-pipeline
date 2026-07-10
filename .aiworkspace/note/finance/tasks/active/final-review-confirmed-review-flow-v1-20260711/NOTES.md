# Final Review Confirmed Review Flow V1 Notes

- Final Review 대상은 Practical Validation Gate 통과 후보로 제한한다.
- 확인 버튼은 새 검증 실행이 아니라 저장된 evidence를 읽을 후보를 명시적으로 확정하는 경계다.
- Review Queue 우선순위 정보는 Decision Desk featured candidate와 `후보 비교 상세`에 남긴다.
- selector option은 `source_type + validation_id / selection_source_id / source_id` stable key이며 label은 표시 전용이다.
- 확정 key와 현재 selector key가 다르면 투자 검토서, Decision Cockpit, Final Decision Action, Evidence Appendix를 렌더링하지 않는다.
- `final_review_level2_review_disposition_v1`의 기존 blocker / warning / open review / monitoring follow-up 계산은 유지하고, 다섯 role별 `role_sections`와 행동 결과를 additive payload로 제공한다.
- 행동 결과는 `점수에 반영됨`, `저장 전 확인`, `Monitoring 조건으로 넘김`, `blocker` 네 의미로 고정한다.
