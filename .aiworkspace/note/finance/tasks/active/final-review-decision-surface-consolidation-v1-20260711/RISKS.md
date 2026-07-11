# Risks

- audit별 row schema와 field 이름이 달라 module adapter가 과도한 추론을 하지 않도록 제한해야 한다.
- standalone Cockpit 제거 시 기존 selected-route blocker와 Monitoring handoff 의미가 최종 판단 영역에서 누락되지 않아야 한다.
- React iframe과 Streamlit form을 한 component처럼 보이게 하되 저장 state ownership은 섞지 않는다.
