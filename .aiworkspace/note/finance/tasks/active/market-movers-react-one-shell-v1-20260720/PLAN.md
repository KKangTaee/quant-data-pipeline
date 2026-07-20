# Market Movers React One-Shell V1 Plan

Status: Approved For Inline Implementation
Last Updated: 2026-07-20

## 이걸 하는 이유?

현재 변동 종목 화면은 React 상단 요약 뒤에 Streamlit 랭킹, 섹터 맥락, 누락 진단, 선택 종목 조사가 순차적으로 붙는다. 사용자는 랭킹에서 종목을 고른 뒤에도 맥락과 조사 화면을 다시 찾아야 한다. 승인된 A안은 이 상태를 `무엇이 움직였는가 → 그 움직임이 어디까지 퍼졌는가 → 선택 종목을 더 조사할 가치가 있는가`라는 한 흐름으로 바꾼다.

## Goal

`market_movers_decision_payload_v1`을 소비하는 단일 React shell을 구현해 ranking, sector/industry flow, bellwether Top 3, quick research, 가격·재무·이벤트 조사를 같은 selected state로 연결한다.

## Scope

- coverage / period / ranking intent / 표시 수를 compact command line으로 제공한다.
- ranking board와 breadth context를 desktop 62/38 비율로 배치한다.
- `Sector | Industry`와 `일 | 주 | 월`을 독립 control로 제공한다.
- group 선택에서 current flow와 시총 Top 3를 연결한다.
- ranking row 선택이 quick research와 expanded research symbol을 바꾼다.
- 상세 조사는 `가격·모멘텀 | 재무 | 뉴스·공시`로 분리한다.
- 재무는 `보고 주기`와 `재무 factor`를 서로 다른 control group으로 표시한다.
- desktop financial chart/readout을 70/30으로 유지하고 좁은 화면에서 stack한다.
- Complete / Partial / Blocked를 user-facing trust line과 local empty state로 표현한다.
- legacy Streamlit surface는 React component unavailable일 때만 fallback으로 유지한다.

## Non-Goals

- sector conditional outlook 확률과 미래 5D/20D/60D 분포
- historical industry forecast
- 매수·매도 추천
- raw job/status/rows 진단 dashboard
- provider direct fetch in React

## Stop Condition

- Python payload/bridge tests와 Market Movers focused contracts가 통과한다.
- React production build가 성공하고 canonical `component_static/`이 갱신된다.
- 실제 desktop과 420px에서 overflow 없이 핵심 interaction을 확인한다.
- QA screenshot 1장 이상을 생성하되 commit하지 않는다.

## Implementation Tasks

### Task 1 — Decision shell payload and selected-state bridge

- [ ] failing tests: wrapper schema, control groups, default selected symbol, group snapshots, financial availability
- [ ] `app/web/overview/market_movers_decision_ui.py`에 pure presentation adapter 구현
- [ ] `app/web/overview_dashboard_helpers.py`에 cached group/research loader 추가
- [ ] `app/web/overview/market_movers_helpers.py`에 all-period group snapshot, selected symbol, one-shell event bridge 구현
- [ ] focused tests와 commit

### Task 2 — One-shell React structure

- [ ] source contract tests에 command/ranking/breadth/quick research/detail 구조 추가
- [ ] `MarketMoversDecisionWorkbench` type과 component 구현
- [ ] legacy component variants는 compatibility branch로 보존
- [ ] ranking/group/detail local interaction과 Streamlit event emit 구현
- [ ] TypeScript build와 commit

### Task 3 — Financial and price chart presentation

- [ ] factor report period와 factor group 독립성 test 추가
- [ ] one-factor-at-a-time financial SVG chart와 unavailable button 구현
- [ ] YTD stored price evidence를 이용한 range-filtered price chart 구현
- [ ] chart/readout 70/30 desktop, mobile stack CSS 구현
- [ ] build/test와 commit

### Task 4 — Page integration and fallback removal

- [ ] React available 경로가 legacy snapshot panel을 중복 렌더링하지 않는 test 추가
- [ ] `render_market_movers_snapshot`을 decision shell 우선으로 전환
- [ ] selected symbol/action event를 Python session state와 연결
- [ ] React unavailable 경로는 기존 Streamlit renderer를 그대로 유지
- [ ] focused regression과 commit

### Task 5 — Browser QA and closeout

- [ ] production component build와 Python compile/pytest 실행
- [ ] 실제 DB smoke로 SP500/Top1000/Top2000 payload 확인
- [ ] desktop/420px interaction, chart balance, overflow Browser QA
- [ ] task docs/root handoff/docs roadmap 동기화
- [ ] generated QA 이미지를 제외하고 commit
