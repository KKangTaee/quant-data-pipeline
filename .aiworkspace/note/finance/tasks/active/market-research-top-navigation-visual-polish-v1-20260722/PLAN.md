# Market Research Top Navigation Visual Polish V1 Plan

Status: Design Approved; Written Spec Review Pending
Last Updated: 2026-07-22

## Goal

Market Research의 승인된 3-family / 7-view 정보 구조는 유지하면서, 상단을 큰 2단 버튼 폼이 아니라 compact research rail로 바꿔 현재 위치와 상하 관계를 즉시 읽게 한다.

## 이걸 하는 이유?

현재 화면은 1차 `st.segmented_control`과 2차 `st.pills`가 모두 full-width outline button으로 보여 두 수준의 위계가 약하다. desktop에서도 버튼 내부 빈 공간이 크고, segmented control의 양 끝과 가운데 모서리가 달라 하나의 제품 navigation보다 입력 form처럼 보인다. 강한 red selected state도 하단 blue-gray workbench와 시각적으로 충돌한다.

## Scope

- page header의 상하 여백과 설명 문구를 compact하게 조정
- 1차 family를 content-width text rail로 표현
- 2차 view를 selected family label과 함께 bounded local navigation surface로 표현
- selected state를 text weight, surface, position으로 함께 구분
- desktop intrinsic width, 760px wrap, 420px 3열/2열 responsive contract
- 기존 query/session/widget, 7-view renderer, Today CTA, Market Movers handoff 보존
- actual Browser QA와 screenshot 1장

## Out Of Scope

- 좌측 drawer / off-canvas / permanent side navigation
- sticky navigation의 즉시 도입
- summary cockpit, 공통 기준일, session banner, Reference panel 추가
- module body, service, loader, DB, provider 계산 변경
- top navigation 외 React workbench redesign

## Tentative Roadmap

### 1차. Written Visual Spec

- 목적: 승인한 compact research rail을 구현 가능한 contract로 고정
- 파일: 이 task의 `PLAN.md`, `DESIGN.md`, `STATUS.md`, `NOTES.md`, `RISKS.md`
- 완료 조건: desktop/mobile hierarchy, state, spacing, scope와 QA 기준이 모호하지 않음

### 2차. Header And Research Rail Implementation

- 목적: header와 두 selector를 서로 다른 visual level로 전환
- 파일: `app/web/overview/page.py`, `app/web/overview/navigation.py`, focused tests
- 완료 조건: 기존 navigation state/route 계약을 유지하면서 full-width box form 인상이 제거됨

### 3차. Browser QA And Sticky Decision

- 목적: 실제 module과 이어지는 간격, 반응형, 선택 상태를 검증
- 파일: tests, task/durable docs; sticky는 QA에서 명확한 필요가 확인될 때만 별도 승인 범위로 남김
- 완료 조건: desktop·760px·420px overflow 0, selected state 판독, 7-view 전환, clean console, screenshot 1장

## Stop Condition

사용자가 written spec을 확인하기 전에는 implementation plan이나 UI code 변경으로 넘어가지 않는다.
