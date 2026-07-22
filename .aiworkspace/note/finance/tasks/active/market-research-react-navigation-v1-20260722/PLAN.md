# Market Research React Navigation V1 Plan

Status: Design Approved
Roadmap: 0/3 implementation stages complete
Last Updated: 2026-07-22

## 이걸 하는 이유?

현재 Market Research 상단은 정보 구조는 올바르지만 제목은 custom HTML, family는 Streamlit segmented control, view는 Streamlit pills로 나뉜다. 이 조합은 Streamlit wrapper 간격과 native widget DOM에 시각 품질이 종속되어 제목·family·view가 하나의 제품 surface처럼 느껴지지 않는다.

상단 전체를 전용 React component로 묶으면 기존 3-family/7-view 상태 계약을 유지하면서 높이, 간격, 선택 상태, hover/focus, mobile layout을 한 디자인 시스템에서 통제할 수 있다.

## Roadmap

1. React component 계약과 Python bridge를 test-first로 구현한다.
2. header/family/view를 하나의 responsive React surface로 구현하고 static bundle을 배포한다.
3. 1280px, 760px, 420px actual Browser QA와 문서 closeout을 수행한다.

## Scope

- 전용 `market_research_navigation` React/Vite component
- compact header, 3-family selector, family-local 7-view selector
- React event -> Python validation -> session/query state bridge
- React bundle unavailable/error 시 현재 Streamlit navigation fallback
- keyboard/focus, reduced-motion, responsive/overflow QA

## Out Of Scope

- module body redesign
- data/service/loader/provider/DB 변경
- drawer, sticky navigation, watchlist, recent/saved research
- Today나 다른 page navigation 변경

## Stop Condition

- React 상단에서 3개 family와 7개 canonical view가 모두 전환된다.
- URL/session/legacy slug/lazy renderer 계약이 기존과 동일하다.
- 1280/760/420px overflow 0과 keyboard focus를 actual Browser QA로 확인한다.
- fallback과 connected Today 회귀가 통과한다.
