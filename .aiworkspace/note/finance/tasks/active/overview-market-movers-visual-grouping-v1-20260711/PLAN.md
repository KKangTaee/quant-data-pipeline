# Overview Market Movers Visual Grouping V1 Plan

## 이걸 하는 이유?

`Sector Breadth`는 제목, 통계, 섹터 카드가 하나의 분석 구간이지만 배경색이 없어 색상 범위가 카드 테두리와 막대에서 끊겨 보인다. 하단의 선택 종목 조사도 종목 선택, 수동 조사 패널, 조사 단서, 기본 지표, 그래프가 같은 업무 흐름인데 여러 독립 박스로 나뉘어 있다. 사용자가 섹터 맥락과 선택 종목 조사 흐름을 한눈에 구분하도록 시각적 그룹을 정리한다.

## 범위

- React와 fallback `Sector Breadth` 전체에 옅은 공통 배경을 적용하고 섹터 lane에는 방향성 tone 배경을 추가한다.
- 선택 종목 조사 전체를 하나의 `종목 조사 워크스페이스` 부모 Streamlit container로 묶는다.
- Ranking Board의 모드별 전체 표 expander를 Ranking Board 부모 container 안으로 옮겨 Sector Breadth와 선택 종목 조사 사이의 독립 박스를 제거한다.
- 부모 그룹 안에서는 중첩 박스 수를 줄이고 section divider, selector, 조사 패널, 단서 tabs, snapshot, chart를 하나의 흐름으로 읽히게 한다.
- 데이터 계산, payload 의미, 조회 action, provider/DB/schema/registry/saved는 변경하지 않는다.

## 완료 조건

- `Sector Breadth` 전체 배경과 lane별 4% direction tint가 React/fallback에서 일치한다.
- 선택 종목 조사 divider부터 조사 단서 tabs와 기본 지표 그래프까지 하나의 keyed parent container 안에 렌더링된다.
- 랭킹 모드별 전체 상세 표가 Ranking Board와 같은 keyed parent 안에 있고 Sector Breadth보다 먼저 렌더링된다.
- desktop/mobile에서 그룹 경계와 내부 간격이 자연스럽고 기존 action/tab 동작이 유지된다.
- 관련 계약 테스트, React production build, py_compile, Browser QA가 통과한다.

## 중단 조건

- Streamlit fragment rerun이 부모 container 경계를 벗어나거나 action 상태를 잃는 회귀가 확인되면 시각 grouping 범위를 축소하고 원인을 기록한다.
