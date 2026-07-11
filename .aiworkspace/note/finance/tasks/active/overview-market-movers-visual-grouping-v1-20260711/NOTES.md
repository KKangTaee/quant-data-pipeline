# Notes

- 이전 `61d1f58a`는 `.ov-mm-list-row`에만 4% tone background를 적용했으며 React Sector Breadth에는 영향을 주지 않았다.
- 종목 조사 하단은 한 workflow지만 현재 `section divider -> selectbox -> React pane -> section divider -> tabs -> snapshot -> chart tabs`처럼 여러 Streamlit/React 렌더 단위로 분리돼 있다.
- raw HTML wrapper를 여러 Streamlit call에 걸쳐 열어 두지 않고, keyed `st.container`가 실제 부모 경계를 소유하게 한다.
- 사용자와 구조를 설명할 때는 가능한 경우 ASCII tree를 사용해 화면 계층을 한눈에 보이게 한다.
- React Sector Breadth의 light surface는 primary blue 3%, lane은 방향 tone 4%로 통일했다. dark surface에서는 lane tint를 8%로 올려 상승/하락 차이가 사라지지 않게 했다.
- keyed workspace는 밝은 Overview surface를 유지하므로 부모가 자체 text color를 소유해 외부 dark theme 상속색 때문에 divider title이 사라지지 않게 했다.
- 선택 종목 조사 상단은 inline divider 대신 `INVESTIGATION WORKSPACE -> 선택 종목 조사 -> 설명`의 독립 헤더로 렌더해 Sector Breadth/Ranking Board와 정보 계층을 맞춘다.
- `모드별 상세 표 전체 높이로 보기`는 Ranking Board/Sector Breadth의 원자료를 펼치는 보조 기능이다. 다음 UI 차수에서는 `Ranking Board -> Sector Breadth -> 선택 종목 조사 -> 상세 데이터 부록` 순서로 내려 핵심 조사 흐름 뒤에 두는 방향이 적절하다.
