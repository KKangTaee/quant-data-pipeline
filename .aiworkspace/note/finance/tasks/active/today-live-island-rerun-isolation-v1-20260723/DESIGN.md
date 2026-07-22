# Today Live Island Rerun Isolation V1 Design

Status: Written specification for user review
Last Updated: 2026-07-23

## 문제 정의

현재 `app/web/today_page.py`의 `@st.fragment(run_every=15)`는 `_render_today_dynamic_body()` 전체를 감싼다. 이 함수는 경제 사이클, S&P 500, 선물 매크로, 심리, 일정, 포트폴리오, 미국 장 일정으로 전체 Today model을 만들고 같은 `today_workbench` component에 다시 전달한다. 15초 heartbeat는 background quote future 완료를 빠르게 감지하려는 의도였지만, fragment 경계가 Today 전체이므로 no-loading 요구를 충족하지 못한다.

React에서는 `TodayWorkbench` 최상위의 `nowMs`가 1초마다 바뀐다. 서버 rerun은 아니고 실제 그래프 path도 바뀌지 않지만, 시장 근거·일정·포트폴리오를 포함한 최상위 tree가 매초 재평가되는 불필요한 결합이다.

## 확인 근거

- 실제 `main-dev` Streamlit 서버에서 periodic 실행 상태가 약 14.9초 간격으로 관찰됐다.
- 한 실행은 약 1초 지속됐고 iframe은 유지됐지만 전체 Today fragment가 다시 계산됐다.
- 1초 샘플에서는 countdown text만 바뀌고 portfolio chart SVG path는 유지됐다.
- 현재 CLOSED 상태에서도 15초 fragment가 계속 실행됐다.

## 검토한 접근

### A. 현재 fragment 유지 + static source cache

전체 source reload 비용은 줄지만 Today 전체 component에 주기적으로 새 payload를 보내는 구조와 Streamlit 실행 표시는 남는다. 증상 완화일 뿐 경계 문제를 해결하지 못해 채택하지 않는다.

### B. Portfolio Live Island 분리 — 채택

Today의 고정 shell과 갱신 가능한 portfolio island를 분리한다. clock은 고정 shell 내부의 작은 child state로 격리하고, server heartbeat는 portfolio island만 소유한다. 기존 Streamlit·DB·collector 구조를 유지하면서 사용자가 지적한 전체 화면 갱신을 제거할 수 있다.

### C. 내부 HTTP API + browser polling 또는 SSE/WebSocket

Streamlit script run 표시까지 완전히 없앨 수 있지만 별도 API lifecycle, authentication/origin, deployment 운영이 추가된다. 이전 승인 범위의 WebSocket/SSE 제외 조건과 YAGNI 원칙에 맞지 않아 이번에는 채택하지 않는다.

## 선택 설계

### 1. Static Today Shell

- 최초 page run에서 전체 Today read model을 한 번 만든다.
- 시장 headline, 세션 일정, 판단 근거, 다음 일정, 다음 행동을 static shell component로 렌더링한다.
- `MarketSessionClock` child만 `setInterval(1000)`을 소유한다.
- phase 계산과 clock/countdown text 외의 subtree는 1초 state를 구독하지 않는다.

### 2. Portfolio Live Island

- 대표 포트폴리오 heading, metrics, graph, contributors, review items를 별도 component mode 또는 별도 declared component로 렌더링한다.
- Python은 initial portfolio payload와 lightweight live payload를 분리한다.
- live heartbeat는 default group context, market session schedule, latest quote/daily dates, EOD close만 읽는다.
- 경제 사이클, S&P 500, 선물 매크로, 심리, 시장 일정은 heartbeat에서 다시 읽지 않는다.
- stable island key를 사용해 iframe을 재생성하지 않고 새 props만 전달한다.

### 3. Heartbeat Activation

- OPEN: 15초 heartbeat로 background quote future 완료와 DB quote 변화를 확인한다.
- CLOSED + EOD waiting/running: bounded handoff 완료 확인 동안만 15초 heartbeat를 유지한다.
- PRE_OPEN, HOLIDAY, WEEKEND, CLOSED+confirmed: 자동 heartbeat를 두지 않는다.
- page를 장시간 열어둔 채 phase 전환이 발생하면 clock child가 phase-transition event를 한 번 Python에 전달해 app/fragment activation 상태를 재평가한다. 매초 event를 보내지 않는다.
- provider collection cadence 300초와 quote stale 600초 계약은 바꾸지 않는다.

### 4. Update Semantics

- portfolio payload가 같으면 island props를 바꾸지 않는다.
- payload가 달라져도 metrics, live point, contributor rows만 React reconciliation으로 변경한다.
- historical EOD curve는 기존 계약대로 불변이며 live point만 추가·교체·제거한다.
- Streamlit full-page spinner, skeleton, loading overlay를 사용하지 않는다.

## 오류 처리

- quote/portfolio live 계산 실패 시 마지막 EOD portfolio payload를 유지한다.
- calendar LIMITED/STALE이면 자동 collection과 phase-transition activation을 막고 일정 제한 상태를 유지한다.
- component event는 allowlist된 navigation 또는 phase-transition event만 처리한다.
- heartbeat 실패가 static Today shell을 지우거나 fallback 전체 HTML로 전환시키지 않는다.

## 테스트 계약

- Python source/behavior test: 전체 Today에 `run_every=15`가 없고 portfolio island만 heartbeat를 소유한다.
- Python test: CLOSED+confirmed에서는 heartbeat가 생성되지 않는다.
- Python test: OPEN과 EOD waiting에서 island tick이 coordinator와 DB overlay만 읽는다.
- React test: 1초 clock tick이 portfolio/chart render counter를 증가시키지 않는다.
- React test: portfolio payload 변경은 metrics/live point를 변경하고 static shell identity를 보존한다.
- Browser QA: CLOSED 화면 20초 관찰에서 Streamlit periodic run 0회, countdown 변화, iframe/graph path 유지.
- Browser QA: controlled OPEN fixture에서 portfolio island만 변경되고 상단 shell과 스크롤/hover가 유지된다.

## 파일 경계

- `app/web/today_page.py`: static shell render와 portfolio heartbeat activation 분리
- `app/web/today_react_component.py`: shell/island component declaration 또는 mode별 render API
- `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`: clock child와 static shell
- 신규 portfolio island React entry/component 또는 기존 component의 명시적 mode 분리
- `tests/test_today_home.py`: Python fragment/read boundary 회귀
- Today React presentation tests: render isolation과 live payload 전환 회귀

## 중요한 Tradeoff

OPEN 중에는 Streamlit이 DB state를 Python에서 읽어야 하므로 작은 portfolio fragment 실행 자체는 남는다. 다만 전체 Today source와 shell을 다시 만들지 않고 island만 갱신하므로 현재의 약 1초 전체 로딩과 화면 재평가는 제거한다. Streamlit 실행 표시 자체를 완전히 없애는 것은 별도 HTTP/push architecture의 후속 과제로 둔다.
