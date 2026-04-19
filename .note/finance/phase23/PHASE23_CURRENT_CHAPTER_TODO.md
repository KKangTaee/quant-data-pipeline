# Phase 23 Current Chapter TODO

## 상태

- `active / first_work_unit_completed`

## 현재 목표

`Phase 23`의 첫 목표는 quarterly strict family를 바로 투자 후보 분석으로 쓰는 것이 아니다.
먼저 현재 구현 상태를 점검하고, annual strict 대비 부족한 제품 기능 차이를 정리한 뒤,
필요한 UI / payload / history / replay 보강으로 들어간다.

## 1. Quarterly Productionization Frame

- `completed` 현재 quarterly strict family 구현 상태 inventory
  - 이미 되는 것, 아직 prototype인 것, annual strict와 다른 것을 분리한다.
- `in_progress` annual strict 대비 missing contract surface 정리
  - real-money contract, guardrail, portfolio handling, rejected-slot/risk-off/weighting 해석이 quarterly에 필요한지 판단한다.
- `completed` Phase 23 first work-unit 문서 작성
  - 첫 작업 단위의 결론을 다음 구현 범위로 바로 이어질 수 있게 정리한다.

## 2. UI / Payload / Replay Hardening

- `pending` quarterly single strategy UI 문구와 경고 정리
  - prototype / research-only / productionizable 상태를 사용자가 오해하지 않게 만든다.
- `pending` compare form override parity 확인
  - quarterly 전략을 compare에 넣었을 때 실제 설정값과 표시 요약이 맞는지 본다.
- `pending` history / load-into-form / saved replay 복원 확인
  - quarterly 실행 결과가 나중에 같은 설정으로 재현되는지 확인한다.

## 3. Validation

- `pending` targeted `py_compile`
- `pending` `.venv` import smoke
- `pending` representative quarterly smoke run
- `pending` manual UI validation checklist handoff

## 4. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` phase plan 실사용 문서로 정리
- `completed` first work-unit 문서 생성
- `completed` glossary / roadmap / doc index / work log / question log sync
- `pending` phase closeout summary 업데이트

## 현재 판단

Phase 23은 열렸고 첫 작업 단위까지 완료했다.
아직 구현 완료 phase는 아니며, 다음 작업은 annual strict 대비 quarterly contract gap을 실제 UI / payload 기준으로 좁히는 것이다.
