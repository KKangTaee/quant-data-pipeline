# Risks

- Lane bar는 현재 선택 coverage/period 내부 상대 스케일이다. 서로 다른 기간 간 절대 비교 차트는 아니다.
- Heatmap을 별도 canvas/chart로 만들지는 않았고, Streamlit HTML/CSS 기반 lane view로 구현했다.
- NASDAQ처럼 유니버스가 비어 있는 coverage에서는 sector map 대신 empty/trust state가 우선한다.
