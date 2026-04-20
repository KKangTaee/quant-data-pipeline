# Phase 24 Current Chapter TODO

## 상태

- `practical_closeout / manual_validation_pending`

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
- `completed` web catalog / single strategy UI 연결
  - 사용자가 `Backtest > Single Strategy`에서 실행할 수 있게 한다.
- `completed` compare / history / saved replay 연결
  - 새 전략이 compare와 재진입 흐름에서 끊기지 않게 한다.

## 3. Validation

- `completed` targeted `py_compile`
- `completed` `.venv` import smoke
- `completed` representative DB-backed smoke run
- `completed` manual validation checklist handoff
- `completed` QA bugfix for default `Global Relative Strength` preset
  - DB 가격 이력이 부족해 이동평균/상대강도 계산 이후 비어버리는 risky ticker는 실행 중단 대신 `excluded_tickers` / 주의사항으로 남기고 제외한다.
- `completed` QA bugfix for malformed price rows and warning copy
  - 단일 결측 가격 행이 이동평균 계산 뒤 날짜를 과도하게 끊지 않도록 `add_ma` 입력을 정리했다.
  - 실행 결과의 "이번 실행에서 같이 봐야 할 주의사항" 문구를 한국어 중심으로 바꿨다.

## 4. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 실사용 문서로 정리
- `completed` first work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` finance comprehensive analysis sync
- `completed` Phase 24 completion / next-phase 문서 업데이트
- `completed` UI / replay integration second work-unit 문서 생성
- `completed` Phase 24 UI replay smoke report 작성

## 현재 판단

Phase 24는 첫 구현 후보 선정, core/runtime first pass,
그리고 `Backtest` UI / compare / history / saved replay 연결까지 완료했다.

다음 작업은 사용자가 `PHASE24_TEST_CHECKLIST.md`로 manual QA를 진행하는 것이다.
체크리스트가 완료되면 Phase 24 closeout 후 Phase 25 진입 여부를 판단한다.
