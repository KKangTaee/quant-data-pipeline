# Overview Lazy Tab Render V20

Status: Active
Started: 2026-06-22

## 이걸 하는 이유?

Overview 첫 진입 때 사용자가 `Market Context`만 보고 있어도 Streamlit `st.tabs` 구조 때문에 Market Movers, Futures Monitor, Sentiment, Sector / Industry, Events, Data Health, Candidate Ops 렌더 함수가 모두 실행된다. 그 결과 DB snapshot / group leadership / futures macro 계산이 한꺼번에 돌며 최초 로딩이 길어진다.

## Scope

- `Workspace > Overview`의 top-level deep tab 렌더링을 선택된 탭 하나만 실행하는 lazy 구조로 바꾼다.
- 기본 선택은 `Market Context`로 유지한다.
- Candidate Ops용 `load_overview_dashboard_snapshot()`은 Candidate Ops가 선택된 경우에만 호출한다.
- 기존 각 탭 내부 UI / 데이터 read model / provider boundary / refresh action behavior는 바꾸지 않는다.

## Steps

1. RED: 선택 탭 dispatch가 하나의 renderer만 호출하고, 기본 진입에서 overview dashboard snapshot을 미리 읽지 않는 테스트를 추가한다.
2. GREEN: top-level `st.tabs`를 segmented/radio 기반 selector + selected renderer dispatch로 교체한다.
3. QA: service contract, py_compile, diff check, Browser QA로 기본 Market Context와 다른 탭 전환을 확인한다.
4. Docs: task docs와 roadmap/index/project map/root logs를 V20 기준으로 동기화한다.

## Stop Condition

- Overview 기본 진입에서 Market Context renderer만 실행된다.
- Market Movers / Futures / Sector / Events / Data Health / Candidate Ops는 선택 시점에만 실행된다.
- Candidate Ops snapshot은 Candidate Ops 선택 전에는 로딩하지 않는다.
- generated screenshots / `.DS_Store` / `.superpowers/`는 stage하지 않는다.
