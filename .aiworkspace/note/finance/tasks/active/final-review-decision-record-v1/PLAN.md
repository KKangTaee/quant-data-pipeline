# Final Review Decision Record V1 Plan

Status: Complete
Started: 2026-05-31

## 이걸 하는 이유?

Final Review의 Candidate Board와 Decision Cockpit은 후보 상태를 먼저 보여주도록 정리됐다. 하지만 실제 최종 판단을 저장하는 입력부는 아직 사용자가 어떤 근거를 보고 어떤 route로 기록해야 하는지 충분히 안내하지 못한다.

이 task는 Final Review의 마지막 사용자 action인 `최종 검토 결과 기록`을 더 명확하게 만든다. 새 검증을 실행하거나 저장 schema를 늘리지 않고, 기존 Decision Cockpit / investability packet / selected-route gate를 decision record checklist와 route별 기록 가이드로 번역한다.

## Goal

- 최종 판단 입력부에 record checklist를 추가해 저장 가능 조건을 미리 보여준다.
- route별 판단 사유 / 운영 전 조건 / 다음 행동 기본 문안을 제공한다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO`는 기존 selected-route gate가 허용할 때만 기록 가능하다는 점을 더 명확히 표시한다.
- 보류 / 거절 / 재검토는 evidence gap이 있어도 기록 가능한 최종 판단 route임을 분리해 보여준다.

## Scope

- `app/services/backtest_evidence_read_model.py`
  - Final Decision Record guide read model
- `app/web/backtest_final_review.py`
  - Decision record checklist / route guide / default text integration
- `tests/test_service_contracts.py`
  - record guide contract tests
- durable flow / roadmap / task docs

## Stop Condition

- Final Review에서 Decision Cockpit 아래 최종 판단 기록부가 checklist와 route guide를 보여준다.
- selected route가 blocked인 경우 사용자가 왜 선정 저장이 막히는지 저장 전 확인할 수 있다.
- 보류 / 거절 / 재검토 route는 blocker가 있어도 기록 가능한 판단으로 안내된다.
- Existing service contract tests and Browser QA pass.
