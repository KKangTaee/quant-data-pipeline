# Runs

## 2026-07-16 Diagnosis Baseline

- `git status --short --branch`, recent commit log 확인.
- finance INDEX / ROADMAP / PROJECT_MAP / SCRIPT_STRUCTURE_MAP / BACKTEST_UI_FLOW / PORTFOLIO_SELECTION_FLOW 확인.
- 2026-07 Practical Validation validation audit와 Final Review evidence closure task 문서 확인.
- current Practical Validation page / workspace / closure / stage role / React component / boundary test source 확인.
- focused baseline:
  - `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_backtest_refactor_boundaries tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationReplayServiceContractTests`
  - result: 66 tests, `OK`.

## 2026-07-16 Design

- B안 Hybrid One-Shell Decision Workspace를 채택했다.
- protected `PRACTICAL_VALIDATION_RESULTS.jsonl`, run history, saved JSONL, generated QA artifact는 수정하거나 stage하지 않았다.
