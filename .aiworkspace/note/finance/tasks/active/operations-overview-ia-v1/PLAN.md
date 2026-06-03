# Operations Overview IA V1 Implementation Plan

## 이걸 하는 이유?

`Operations`에는 portfolio monitoring, system/data health, archive/recovery 성격의 화면이 같은 레벨로 섞여 있다. Selected Portfolio Dashboard의 위치는 유지하되, Operations의 첫 화면과 navigation label을 정리해 사용자가 현재 확인할 운영 상태와 보조 도구를 빠르게 구분하게 만든다.

## Scope

- Add a lightweight `Operations Overview` landing page.
- Keep existing pages and routes; do not delete legacy tools.
- Rename navigation labels to clarify primary and archive roles while preserving URL paths.
- Add a small selected-dashboard monitoring status summary where it supports the new IA.
- Update durable docs after implementation.

## Out Of Scope

- Broker/account sync, live approval, order tickets, auto rebalance.
- Registry or saved JSONL schema changes.
- React/API migration.
- Deleting Backtest Run History or Candidate Library.

## Files

| File | Action | Purpose |
| --- | --- | --- |
| `tests/test_service_contracts.py` | Modify | Add TDD coverage for Operations Overview read model. |
| `app/web/operations_overview.py` | Create | Streamlit-free model builder plus page renderer for Operations Overview. |
| `app/web/streamlit_app.py` | Modify | Add Operations Overview page and clarify Operations navigation labels. |
| `app/web/final_selected_portfolio_dashboard.py` | Modify | Add small monitoring-position language/status support if needed. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Modify | Document Operations Overview / Archive-Recovery IA. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Modify | Clarify Selected Dashboard remains Operations portfolio monitoring. |
| `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` | Modify | Register `app/web/operations_overview.py`. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Modify | Add Operations Overview entry and updated Operations boundary. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Modify | Record implementation focus completion. |
| `.aiworkspace/note/finance/WORK_PROGRESS.md` | Modify | Short handoff milestone. |
| `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | Modify | Short user request / decision record. |

## TDD Tasks

1. Write failing tests for `build_operations_overview_model`.
2. Verify RED with targeted unittest.
3. Implement minimal read model and renderer.
4. Verify GREEN with targeted unittest and compile.
5. Add navigation and copy changes.
6. Run focused tests and Browser QA.
7. Sync docs and commit one coherent implementation unit.
