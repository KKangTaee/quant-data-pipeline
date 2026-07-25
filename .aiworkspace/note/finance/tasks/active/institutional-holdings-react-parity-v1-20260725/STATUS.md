# Institutional Holdings React Parity V1 Status

Status: Design Review
Started: 2026-07-25

## Progress

- 2026-07-25: Request classified as a focused multi-step Institutional Holdings UI task.
- 2026-07-25: Existing completed Institutional context-first task, current Python / React ownership, and Today / Market Research patterns reviewed.
- 2026-07-25: Actual 1280px and 420px render comparison confirmed duplicate Streamlit / React shell, visual-token drift, navigation mismatch, manager-control competition, and delayed mobile first-read.
- 2026-07-25: User approved the direction that the normal user-facing surface should follow Today / Market Research: React owns the complete visible page while Streamlit remains a thin route / data / event / fallback adapter.
- 2026-07-25: Written design drafted for React ownership, component boundaries, event states, visual parity, responsive behavior, fallback and QA.

## Current Step

전체 roadmap `1/4차` complete.

`2차 React 전면 디자인과 component boundary` written spec을 사용자 검토에 올리는 단계다. 구현 코드는 아직 변경하지 않았다.

## Next Action

사용자가 `DESIGN.md`를 승인하면 `superpowers:writing-plans` 절차로 focused implementation plan을 작성한다.

## Current Scope Boundary

- 정상 화면 UI는 React가 소유한다.
- Streamlit route, DB / service calls, explicit server events and fallback은 유지한다.
- standalone SPA / new HTTP API / DB schema / ingestion change는 이번 task 밖이다.
