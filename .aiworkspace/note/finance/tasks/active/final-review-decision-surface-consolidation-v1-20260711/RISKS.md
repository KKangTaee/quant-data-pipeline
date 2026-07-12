# Risks

- audit별 row schema와 field 이름이 달라 module adapter가 과도한 추론을 하지 않도록 제한해야 한다.
- standalone Cockpit 제거 시 기존 selected-route blocker와 Monitoring handoff 의미가 최종 판단 영역에서 누락되지 않아야 한다.
- React iframe과 Streamlit form을 한 component처럼 보이게 하되 저장 state ownership은 섞지 않는다.

## Closeout

- 최신 Distinct Strategy / GRS validation의 적용 가능한 REVIEW trace가 모두 derived 또는 qualitative로 분류되고 missing contract가 first-read에 남지 않음을 확인했다.
- 판단 저장은 기존 Python append-only registry boundary를 유지하며 React intent나 자동 실행을 추가하지 않았다.
- 다음 실험을 실제 Backtest Analysis 설정으로 복사하는 기능은 구현하지 않았고, 현재는 명시적인 정보 / 가설로만 남는다.
