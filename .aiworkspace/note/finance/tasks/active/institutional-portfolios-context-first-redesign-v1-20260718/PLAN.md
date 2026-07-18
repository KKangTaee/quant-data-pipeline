# Institutional Portfolios Context-First Redesign V1 Plan

Status: Implementation In Progress
Started: 2026-07-18

## 이걸 하는 이유?

`Workspace > Institutional Portfolios`는 기관 검색, allocation donut, 가정 성과, 분기 변화, 섹터 노출, 전체 보유, 종목 차트, 보유 기관 역조회까지 기능 범위가 넓다.
하지만 현재 첫 화면은 선택 기관의 포트폴리오 특징보다 검색 rail, freshness, 여러 panel이 먼저 보여 사용자가 핵심 맥락을 직접 조합해야 한다.

또한 `전체 보유`는 React에서 최대 80개만 조용히 잘라 표시하고, primary React 화면에는 직접 종목 검색이 없으며, CUSIP-symbol mapping coverage가 낮은 기관은 종목명·섹터·차트 연결이 크게 제한된다.
이번 작업은 그래프를 없애는 것이 아니라 Overview `시장 맥락`의 결론-근거-세부 흐름을 적용하고, 모든 13F 보유 row가 탐색 가능한 계약을 만드는 것이 목적이다.

## 전체 Roadmap

### 1차: 현재 기능 / UI / 데이터 노출 감사

- 목적: 화면 기능, code/data ownership, 실제 DB coverage, 종목 미노출 원인을 분리한다.
- 완료 조건: UI 절단, 직접 검색 부재, mapping coverage, 이전 분기 부재를 구현 사실과 actual DB evidence로 확인한다.
- 상태: 완료.

### 2차: 맥락 우선 설계 확정

- 목적: 선택 기관의 포트폴리오 맥락을 첫 화면의 주인공으로 두고, 종목 노출과 데이터 상태 계약을 고정한다.
- 화면 / 파일 범위: task `DESIGN.md`, 향후 `app/services/institutional_portfolios.py`, `app/web/institutional_portfolios.py`, Institutional Portfolios React workbench.
- 완료 조건: 정보 구조, payload, 상태, 오류, responsive, QA 계약을 사용자가 승인한다.
- 상태: 완료. 사용자가 Context-First written spec을 승인했다.

### 3차: 기능 정확성 / 노출 계약과 Context-First UI 구현

- 목적: 종목 누락과 의미 충돌을 먼저 닫고 Overview 계열 시각 문법으로 화면을 재구성한다.
- 예상 범위:
  - 전체 보유 검색 / 필터 / 정렬 / pagination.
  - React primary surface의 종목 직접 검색.
  - mapping count / weight coverage와 unresolved state.
  - 이전 분기 없음 상태의 change board suppression.
  - 선택 기관 context hero와 section flow.
- 완료 조건: focused TDD, React build, actual DB smoke, desktop / 420px Browser QA.
- 상태: 현재 차수. `IMPLEMENTATION_PLAN.md` 기준 TDD 구현과 QA를 진행한다.

### 4차: 실사용 미세 조정 / 데이터 깊이 / 문서 closeout

- 목적: 실제 대형 기관과 미매핑 비중이 높은 기관에서 탐색성을 보정하고, 과거 분기 backfill 필요성을 별도 승인 범위로 판정한다.
- 예상 범위: Berkshire / Bridgewater / Duquesne actual QA, interaction density, long-list performance, durable docs alignment.
- 완료 조건: 사용 흐름 QA, 남은 mapping / historical coverage gap 명시, 문서와 root handoff 정렬.
- 상태: 미착수.

## 이번 설계에서 하지 않는 일

- 새로운 외부 provider 또는 유료 13F API 도입.
- OpenFIGI / licensed security master adapter 구현.
- SEC historical quarter 자동 backfill 실행.
- 추천, 매수 / 매도 신호, live trading, broker order, auto rebalance.
- 운영 run / job / row 진단 panel 추가.
- 기존 custom 가격 차트를 새 chart library로 교체.

## Stop Condition

- `DESIGN.md`가 사용자 workflow, data correctness, payload/state, file ownership, validation contract를 모두 포함한다.
- 설계 자체 검토에서 미완성 항목, 범위 모순, 숨은 데이터 절단 계약이 없다.
- 사용자가 written spec을 승인하기 전에는 implementation plan이나 코드 변경으로 넘어가지 않는다.
