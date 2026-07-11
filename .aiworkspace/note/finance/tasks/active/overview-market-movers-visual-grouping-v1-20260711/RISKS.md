# Risks

- React custom component는 iframe이므로 Streamlit parent container와 내부 DOM을 공유하지 않는다. visual grouping은 Streamlit parent surface와 iframe 내부 padding/background의 조합으로 맞춘다.
- fragment/iframe은 keyed parent 안에 유지되며 Browser QA에서 selector, 조사 단서, Snapshot, graph가 같은 부모에 존재함을 확인했다.
- light 3~4% tint와 dark lane 8% tint를 실제 화면에서 확인했다.
- Open UX follow-up: `모드별 상세 표 전체 높이로 보기` expander를 선택 종목 조사 뒤의 하단 상세 데이터 부록으로 옮기는 개선은 사용자 승인 후 별도 적용한다.
- 조회 action/data payload/provider 경계는 변경하지 않았다.
