# Institutional Holdings React Parity V1 Plan

Status: Design Review
Started: 2026-07-25

## 이걸 하는 이유?

`Institutional Holdings`는 기관 검색, allocation, 전체 보유 탐색, 분기 변화, sector exposure, 가정 성과, 종목 검색, 가격 차트, 보유 기관 역조회까지 필요한 기능이 이미 충분하다.

문제는 정상 화면 위에 Streamlit `title` / caption / contextual-help expander / refresh expander / detailed fallback이 남아 있고, React workbench도 8px card와 강한 segmented tab 중심으로 구성되어 최근 `Today`와 `Market Research`의 React-owned shell, blue-gray surface, 명확한 reading hierarchy와 다르게 보인다는 점이다.

이번 작업은 기능을 다시 만드는 것이 아니라 사용자가 보는 정상 화면의 소유권을 React로 통일하고, 기존 기능을 유지한 채 제품 전체의 최신 시각 문법과 interaction 경계를 맞추는 전면 UI 개편이다.

## Agreed Direction

- `Today`와 `Market Research`처럼 Streamlit은 route, DB read-model, explicit server event, fallback만 소유한다.
- 정상 상태에서 보이는 page header, navigation, manager switcher, data status, refresh, help, caveat, portfolio/security workspace는 React가 소유한다.
- 세 가지 visual companion 시안 중 `C · Modular Research Studio`를 최종 방향으로 사용한다.
- desktop은 기관·리서치 전환을 상시 노출하는 React-owned research rail과 main canvas를 사용하고, mobile은 같은 기능을 compact top switcher / drawer로 접는다.
- Today / Market Research의 blue-gray token, radius, typography는 유지하되 layout은 기관 탐색 빈도가 높은 전문 research studio에 맞춘다.
- 별도 React SPA, 신규 public API, DB schema 변경은 만들지 않는다.
- 기존 institutional 기능과 SEC / DB / loader correctness boundary는 유지한다.

## 전체 Roadmap

### 1차: 현재 UI / architecture 진단

- 목적: Today / Market Research와 Institutional Holdings의 화면 소유권과 visual hierarchy 차이를 확인한다.
- 범위: 관련 task 기록, Python page wrapper, React TSX/CSS, desktop / 420px actual render.
- 완료 조건: 기능 문제가 아닌 shell duplication, token drift, navigation mismatch, mobile first-read delay를 evidence로 확인한다.
- 상태: 완료.

### 2차: React 전면 디자인과 component boundary 확정

- 목적: 정상 화면에서 React가 소유할 영역과 Streamlit adapter / fallback 경계를 written spec으로 고정한다.
- 범위: `C · Modular Research Studio`, research rail / main canvas, component map, payload / event / responsive / QA contract.
- 완료 조건: placeholder와 모순이 없는 written spec을 사용자가 승인한다.
- 상태: draft 작성 중.

### 3차: React shell / component 분리 / visual parity 구현

- 목적: 기존 기능을 보존하면서 공통 visual token 위에 Institutional 전용 research rail / main canvas layout을 구현한다.
- 예상 범위:
  - `app/web/institutional_portfolios.py`
  - `app/web/institutional_portfolios_react_component.py`
  - `app/web/streamlit_components/institutional_portfolios_workbench/src/`
  - focused Python / React tests
- 완료 조건: normal path React ownership, explicit event boundary, fallback preservation, focused automated checks 통과.
- 상태: pending.

### 4차: actual interaction QA / documentation closeout

- 목적: 실제 DB-backed manager / holdings / security 흐름과 desktop / tablet / mobile 시각 일관성을 검증한다.
- 완료 조건:
  - Berkshire / Bridgewater actual flow.
  - manager selection, holdings search/filter/page, mapped/unmapped security, chart, refresh/help disclosure.
  - 1280px / 760px / 420px overflow와 console 확인.
  - durable docs / root handoff 정렬과 coherent commit.
- 상태: pending.

## In Scope

- 정상 화면의 Streamlit visual shell 제거.
- React-owned page header, manager workspace, refresh/help/caveat presentation.
- desktop research rail과 tablet/mobile adaptive manager / view switcher.
- Institutional workbench component 분리와 state ownership 정리.
- Today / Market Research visual token과 responsive grammar 적용.
- 기존 기능과 payload 의미를 유지하는 event contract 보강.
- React unavailable / data unavailable fallback 보존.

## Out Of Scope

- Streamlit routing 자체 제거.
- 독립 React SPA 또는 Python HTTP API 신설.
- SEC 13F collector, DB schema, loader, OpenFIGI mapping 변경.
- historical quarter backfill.
- 신규 추천, 매수 / 매도 신호, live trading, broker action.
- 새로운 운영 job / row / diagnostic dashboard.
- chart library 교체.
- Today / Market Research의 역방향 refactor.

## Stop Condition

- Written spec이 사용자에게 승인되지 않으면 구현을 시작하지 않는다.
- 기존 기능을 삭제하거나 data / workflow 의미를 바꿔야 하는 새 요구가 나오면 roadmap을 갱신하고 다시 확인한다.
