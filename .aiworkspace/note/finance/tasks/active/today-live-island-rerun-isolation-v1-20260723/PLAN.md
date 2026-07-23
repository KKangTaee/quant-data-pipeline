# Today Live Island Rerun Isolation V1 Plan

Status: Design approved in conversation; written specification review pending
Roadmap: 0/2 implementation stages complete
Last Updated: 2026-07-23

## 이걸 하는 이유?

Today의 장중 포트폴리오 자동 갱신은 5분 시세 수집을 자연스럽게 보여주기 위한 기능이지만, 현재 15초 fragment가 Today 전체 read model과 전체 React workbench를 다시 실행한다. 실제 브라우저에서 약 15초마다 Streamlit 실행 상태가 약 1초 노출됐고, 장이 끝난 뒤에도 같은 실행이 반복됐다. 사용자가 보는 시장 판단·일정·확정 종가 화면은 고정하고, 갱신이 필요한 시계와 장중 포트폴리오만 작은 경계에서 바꾸도록 수정한다.

## Roadmap

### 1/2차 — 전체 rerun 제거

- Today 전체를 감싼 `run_every=15` fragment를 제거한다.
- 1초 clock/countdown state를 시장 세션 전용 React child로 격리한다.
- 시장 근거, 일정, 포트폴리오 그래프가 시계 때문에 매초 재평가되지 않도록 경계를 고정한다.
- 정규장 OPEN 또는 close handoff가 아닌 상태에서는 자동 server heartbeat를 실행하지 않는다.

완료 조건: CLOSED Today를 20초 이상 열어도 Streamlit periodic run 상태가 나타나지 않고, 시계·countdown은 계속 움직인다.

### 2/2차 — Portfolio Live Island

- 장중 평가액·수익률·기여도·그래프만 별도 React component/fragment 경계에서 갱신한다.
- heartbeat는 OPEN quote completion과 bounded EOD handoff에 필요한 동안만 동작한다.
- heartbeat는 DB-backed portfolio context와 quote/EOD state만 읽고 Today의 다른 시장 source를 다시 읽지 않는다.
- provider 수집 cadence는 기존 300초, DB stale 기준은 기존 600초를 유지한다.

완료 조건: 장중 payload 변경 시 포트폴리오 영역만 자연스럽게 바뀌고, 상단 시장 판단·근거·일정 DOM과 사용자 스크롤/hover 상태는 유지된다.

## 범위 밖

- 별도 FastAPI 서버, SSE, WebSocket, 브라우저의 provider 직접 호출
- 프리마켓·애프터마켓
- 포트폴리오 계산·DB schema·수집 cadence 변경
- Today 정보 구조나 시각 디자인의 재편

## Stop Condition

두 단계 구현, 자동 회귀, 실제 CLOSED Browser QA를 완료하고, 실제 OPEN 확인이 시간상 불가능하면 deterministic OPEN fixture 결과와 남은 실측 gap을 명시한다.
