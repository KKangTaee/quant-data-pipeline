# Phase 23 Current Chapter TODO

## 상태

- `active / portfolio_handling_contract_first_pass_completed`

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
- `pending` saved replay UI-level manual 확인
  - saved replay가 같은 contract 값을 유지하는지 실제 UI에서 확인한다.

## 3. Validation

- `completed` targeted `py_compile`
- `completed` `.venv` import smoke
- `pending` representative quarterly smoke run
- `pending` manual UI validation checklist handoff

## 4. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 실사용 문서로 정리
- `completed` first work-unit 문서 생성
- `completed` glossary / roadmap / doc index / work log / question log sync
- `completed` second work-unit 문서 생성
- `pending` phase closeout summary 업데이트

## 현재 판단

Phase 23은 quarterly portfolio handling contract first pass까지 완료했다.
아직 구현 완료 phase는 아니며, 다음 작업은 대표 quarterly smoke run과 saved replay 흐름 검증이다.
