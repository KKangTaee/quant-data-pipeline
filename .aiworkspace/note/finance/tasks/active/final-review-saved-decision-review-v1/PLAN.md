# Final Review Saved Decision Review V1 Plan

Status: Complete
Started: 2026-05-31

## 이걸 하는 이유?

Final Review는 Candidate Board, Decision Cockpit, Final Decision Record까지 정리됐다. 남은 내부 완성도 gap은 저장 후 확인 화면이다.

사용자가 `최종 검토 결과 기록`을 남긴 뒤에는 단순 JSON 또는 flat table이 아니라, 어떤 판단이 몇 건인지, 어떤 row가 Selected Dashboard로 이어질 수 있는지, 최근 판단의 이유와 evidence 상태가 무엇인지 빠르게 다시 읽을 수 있어야 한다.

## Goal

- 저장된 Final Decision V2 row를 decision ledger처럼 요약한다.
- selected / hold / reject / re-review counts와 latest decision을 보여준다.
- route filter와 focused detail tabs로 저장된 판단을 빠르게 확인한다.
- 기존 Decision Dossier export를 유지하되, saved decision review의 일부로 더 명확히 배치한다.
- 새 registry, report auto-write, validation rerun, live approval / order behavior는 만들지 않는다.

## Scope

- `app/services/backtest_evidence_read_model.py`
  - saved decision review read model
- `app/web/backtest_final_review.py`
  - saved decision summary / filter / detail tabs UI
- `tests/test_service_contracts.py`
  - saved decision review contract tests
- durable flow / roadmap / task docs

## Stop Condition

- Final Review saved decision section shows summary counts before the table.
- Saved decisions can be filtered by route family.
- Detail view clearly shows status, operator decision, components, dossier, evidence packet, raw JSON.
- Existing service contract tests pass.
- Browser QA confirms the saved decision review section renders.
