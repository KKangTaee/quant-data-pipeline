# Phase 23 Current Chapter TODO

## 상태

- `manual_validation_feedback_in_progress`

## 현재 목표

`Phase 23`의 첫 목표는 quarterly strict family를 바로 투자 후보 분석으로 쓰는 것이 아니다.
먼저 현재 구현 상태를 점검하고, annual strict 대비 부족한 제품 기능 차이를 정리한 뒤,
필요한 UI / payload / history / replay 보강으로 들어간다.

## 1. Quarterly Productionization Frame

- `completed` 현재 quarterly strict family 구현 상태 inventory
  - 이미 되는 것, 아직 prototype인 것, annual strict와 다른 것을 분리한다.
- `completed` annual strict 대비 portfolio handling contract surface first pass
  - real-money contract, guardrail, portfolio handling, rejected-slot/risk-off/weighting 해석이 quarterly에 필요한지 판단한다.
- `completed` Phase 23 first work-unit 문서 작성
  - 첫 작업 단위의 결론을 다음 구현 범위로 바로 이어질 수 있게 정리한다.

## 2. UI / Payload / Replay Hardening

- `completed` quarterly single strategy portfolio handling UI first pass
  - quarterly 3개 family에 `Portfolio Handling & Defensive Rules`와 Phase 23 상태 안내를 추가했다.
- `completed` compare form portfolio handling override first pass
  - quarterly 전략을 compare에 넣었을 때 `Weighting`, `Rejected Slot Handling`, `Risk-Off` contract를 고를 수 있게 했다.
- `completed` history / load-into-form contract restore first pass
  - quarterly 실행 결과를 form으로 다시 불러올 때 portfolio handling contract 값이 복원되게 했다.
- `completed` history / saved replay contract roundtrip code check
  - result bundle meta, history record, history payload, saved portfolio strategy override가 quarterly portfolio handling contract 값을 보존하는지 확인했다.
- `completed` compare variant immediate refresh 보강
  - compare family variant 선택을 form 밖으로 이동해 Annual / Quarterly 변경 시 세부 입력 UI가 즉시 갱신되게 했다.
- `completed` compare 공용 입력 / 전략별 입력 구조 정리
  - `Start Date`, `End Date`, `Timeframe`, `Option`을 `Compare Period & Shared Inputs`로 모으고,
    기존 `Advanced Inputs` form wrapper 없이 `Strategy-Specific Advanced Inputs`가 바로 갱신되게 했다.
- `pending` saved replay UI-level manual 확인
  - saved replay가 같은 contract 값을 유지하는지 실제 UI에서 확인한다.

## 3. Validation

- `completed` targeted `py_compile`
- `completed` `.venv` import smoke
- `completed` representative quarterly smoke run
  - `AAPL / MSFT / GOOG`, 2021-01-01~2024-12-31, non-default portfolio handling contract 조합으로 quarterly 3개 family를 실제 DB-backed runtime에서 실행했다.
  - smoke run 중 공통 result bundle meta에 `weighting_mode`, `rejected_slot_handling_mode`, `rejected_slot_fill_enabled`, `partial_cash_retention_enabled`가 빠지는 문제를 발견하고 수정했다.
- `completed` manual UI validation checklist handoff
  - `PHASE23_TEST_CHECKLIST.md` 기준으로 사용자가 직접 UI를 확인하면 된다.

## 4. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 실사용 문서로 정리
- `completed` first work-unit 문서 생성
- `completed` glossary / roadmap / doc index / work log / question log sync
- `completed` second work-unit 문서 생성
- `completed` representative smoke report 생성
- `completed` third work-unit 문서 생성
- `completed` fourth work-unit 문서 생성
- `completed` phase closeout summary 업데이트

## 현재 판단

Phase 23은 quarterly portfolio handling contract first pass, representative DB-backed smoke run,
history / saved replay contract roundtrip code check,
compare variant immediate refresh와 compare 입력 구조 정리까지 완료했다.
현재는 사용자의 Phase 23 checklist QA 피드백을 반영하는 중이며,
다음 확인은 수정된 Compare variant / shared-input UI와 checklist 문구가 실제 QA에 충분한지 보는 것이다.
