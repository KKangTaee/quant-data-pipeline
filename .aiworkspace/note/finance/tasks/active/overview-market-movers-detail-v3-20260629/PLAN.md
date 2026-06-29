# Overview Market Movers Detail V3 Plan

## 이걸 하는 이유?

2차에서 Market Movers는 탐색 모드를 갖췄지만, 사용자가 한 종목을 고른 뒤 왜 더 봐야 하는지 확인하는 흐름은 아직 하단 외부 링크 부록에 가깝다. 3차는 선택 종목 조사 패널을 detail workflow로 정리해 symbol / rank / movement / sector / metadata state / research links를 한 곳에서 보게 한다.

## Scope

- 선택 모드의 symbol rows에서 selectbox 기반 종목 선택 UX를 유지한다.
- 선택 종목 detail 영역에 identity, ranking context, movement / volume context, 같은 섹터 내 간단 peer context를 표시한다.
- 기존 `app/services/overview/why_it_moved.py` read model과 metadata status strip을 UI에 연결한다.
- News / Korean News / SEC metadata 상태는 session-only strip으로 보여준다.
- `간단 메타데이터 조회`는 선택 종목 1개에 한해 기존 service boundary를 통해 실행하며, DB / registry / saved setup에는 저장하지 않는다.
- external links는 `조사 단서 > 외부 검색` 안의 clickable table로 유지한다.

## Out Of Scope

- 자동 원인 판정, catalyst score, confidence score, trade score.
- AI 요약, 기사 본문 저장, 공시 본문 저장, persistent investigation history.
- Why It Moved 독립 Overview top-level tab.
- 4차 sector heatmap / breadth 개편.
- 5차 coverage trust/data quality UX 정리.

## Stop Condition

- RED/GREEN service contract tests로 selected-symbol detail workflow를 검증한다.
- 공통 검증 명령과 fallback tests를 실행한다.
- Streamlit Browser QA에서 SP500 daily, SP500 weekly/monthly 중 하나, NASDAQ coverage 상태, 좁은 화면을 확인한다.
- QA screenshot 1장을 확보하되 stage하지 않는다.
- coherent Korean commit을 만든 뒤 4차 진행 전 멈춘다.
