# Market Research IA Redesign V1 Plan

Status: Design Approved; Written Spec Review Pending
Last Updated: 2026-07-22

## Goal

기존 `Overview` 최초 화면 구조를 `Today` 이후의 `Market Research` deep-research workspace로 재정의한다. 사용자가 시장 환경, 지수 가치평가, 종목 리서치 중 목적을 먼저 선택하고 기존 DB-backed module을 같은 근거와 URL 호환성으로 사용할 수 있게 한다.

## 이걸 하는 이유?

`Today`가 경제사이클, S&P 500, 선물 매크로, 심리, 일정을 compact summary로 제공하지만 Market Research는 여전히 `Overview` 제목, 공통 장 세션 banner, 다섯 개 동급 tab을 유지한다. 이 구조는 Today와 역할이 겹치고 시장 수준 질문과 종목 수준 질문을 혼합하며 실제 research module을 첫 화면 아래로 밀어낸다.

## Scope

- page identity를 `Overview`에서 `Market Research`로 정렬
- 목적형 1차 navigation: `시장 환경 | 지수 가치평가 | 종목 리서치`
- 문맥형 2차 navigation
  - 시장 환경: 경제 사이클, 선물 매크로, 심리, 일정
  - 지수 가치평가: S&P 500
  - 종목 리서치: 변동 종목, 미국 개별주식
- 공통 장 session banner와 Reference contextual help의 page-top 반복 제거
- module별 기준일, 자료상태, refresh action 소유권 유지
- 변동 종목 선택 symbol을 미국 개별주식 분석으로 넘기는 explicit handoff
- 기존 `/overview`, `overview_tab` deep link와 Today CTA 호환
- desktop, 760px, 420px Browser QA

## Out Of Scope

- 새로운 시장 summary, 종합 점수, cockpit 추가
- Economic Cycle, S&P 500, Futures Macro, Sentiment, Events 계산 변경
- provider, DB schema, ingestion cadence 변경
- 별도 `Stock Research` 상위 page 신설
- live trading, validation gate, monitoring signal
- run/job/row 진단 panel 추가

## Tentative Roadmap

### 1차. Market Research Shell

- 목적: Overview 흔적과 상단 중복 제거
- 파일: `app/web/overview/page.py`, `app/web/overview/navigation.py`
- 완료 조건: 새 title/purpose와 3개 목적형 selector가 표시되고 기존 module 진입이 가능함

### 2차. Module Regrouping And Compatibility

- 목적: 7개 module을 새 family/view 구조에 연결
- 파일: `app/web/overview/navigation.py`, `app/web/overview/market_context.py`, 관련 focused tests
- 완료 조건: legacy query/session state를 새 view로 안전하게 정규화하고 모든 module이 단독 deep link로 열림

### 3차. Research Handoff And Header Ownership

- 목적: 변동 종목 발견에서 개별주식 분석까지 실제 업무 흐름 연결
- 파일: `app/web/overview/market_movers_helpers.py`, `app/web/overview/market_context_helpers.py`, `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`
- 완료 조건: 현재 선택 ranking row와 일치하는 symbol을 유지해 개별주식 분석으로 이동하고 장 session/reference/refresh 정보가 owning module에만 표시됨

### 4차. Responsive QA And Documentation Sync

- 목적: 실제 사용 환경과 durable docs 정렬
- 파일: tests, finance docs/flows/project map/task/root handoff logs
- 완료 조건: automated regression, desktop/760px/420px actual Browser QA, screenshot 1장, no horizontal overflow, existing Today CTA/deep link continuity

## Stop Condition

설계 문서에 대한 사용자 검토가 끝나기 전에는 implementation plan이나 code edit로 진행하지 않는다.
