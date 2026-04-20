# Phase 24 Current Chapter TODO

## 상태

- `implementation_in_progress / core_runtime_first_pass_completed`

## 현재 목표

`Phase 24`의 목표는 새 전략을 성과 분석 대상으로 바로 고르는 것이 아니다.
먼저 `quant-research` 전략 문서가 finance 백테스트 제품 기능으로 들어오는 표준 경로를 만들고,
그 기준에 맞는 첫 신규 전략 family를 구현한다.

## 1. Research-To-Implementation Bridge

- `completed` 구현 후보 선정 기준 정의
  - 가격 데이터만으로 가능한 전략, 추가 데이터가 필요한 전략, 나중에 미룰 전략을 나눈다.
- `completed` 첫 구현 후보 선정
  - 현재 1순위 후보는 `Global Relative-Strength Allocation With Trend Safety Net`이다.
- `completed` first work-unit 문서 작성
  - 왜 이 후보가 Phase 24 첫 구현 후보인지 기록한다.

## 2. First New Family Implementation

- `completed` strategy / sample / runtime 최소 구현
  - 신규 전략 simulation 또는 기존 engine 재사용 경로를 명확히 만든다.
- `completed` core/runtime smoke report 작성
  - `PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`에 compile / import / DB-backed smoke 결과를 기록한다.
- `pending` web catalog / single strategy UI 연결
  - 사용자가 `Backtest > Single Strategy`에서 실행할 수 있게 한다.
- `pending` compare / history / saved replay 연결
  - 새 전략이 compare와 재진입 흐름에서 끊기지 않게 한다.

## 3. Validation

- `completed` targeted `py_compile`
- `completed` `.venv` import smoke
- `completed` representative DB-backed smoke run
- `pending` manual validation checklist handoff

## 4. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 실사용 문서로 정리
- `completed` first work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` finance comprehensive analysis sync
- `completed` Phase 24 completion / next-phase 문서 업데이트

## 현재 판단

Phase 24는 첫 구현 후보 선정과 core/runtime first pass까지 완료했다.
다만 아직 제품 UI에 노출된 전략은 아니다.

다음 작업은 `Global Relative Strength`를 catalog, single strategy UI,
compare, history, saved replay까지 연결하는 것이다.
