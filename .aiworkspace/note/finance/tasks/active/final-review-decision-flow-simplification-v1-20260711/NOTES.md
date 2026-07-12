# Notes

- 현재 `판단 기록`은 React report 전체 뒤에 있고, Evidence Appendix와 Saved Decisions가 다시 이어진다.
- Evidence Appendix의 Practical Validation / robustness / investability 내용은 report 상세 trace 또는 이전 stage와 중복된다.
- Saved Decisions의 selected route는 Portfolio Monitoring이 운영 확인을 소유하며, non-select route는 audit row 보존만 필요하다.
- React submit payload는 `record_final_decision` intent id, route, 사용자가 쓴 reason만 포함한다.
- Decision ID, constraints, next action은 Python session / route template에서 자동 생성하며 component payload에 노출하지 않는다.
- 같은 component intent가 rerun 뒤 재전달돼도 source별 consumed intent id로 중복 append를 막는다.
