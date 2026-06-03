# Operations Console Restructure V2-V5 Plan

## 이걸 하는 이유?

사용자는 Operations 탭 개편을 단계별로 요청했지만, 1차 구현은 navigation / landing page 보강에 가까웠다. 이번 task는 남은 2차~5차를 한 작업 흐름으로 묶어, Operations가 단순 링크 모음이 아니라 선정 후 portfolio monitoring과 system/data health를 우선으로 보여주는 운영 콘솔로 읽히게 만든다.

## Overall Roadmap

| Stage | Goal | Completion Criteria |
| --- | --- | --- |
| 1차 | Operations 큰 뼈대 정리 | `Operations Overview`, `Portfolio Monitoring`, `System / Data Health`, `Archive / Recovery` lane이 생김. 완료됨. |
| 2차 | 기능 감사와 유지 / 개선 / 격하 결정 | Operations Overview model에 surface audit decision과 stage roadmap이 들어가고, task 문서에 유지 / 개선 / 격하 기준이 남음. |
| 3차 | 리밸런싱 의미 정정 | Portfolio Monitoring의 rebalance table이 주문 지시처럼 읽히지 않고, target snapshot / next review / no order boundary를 명확히 표시함. |
| 4차 | Archive / Recovery 정리 | Backtest Run History와 Candidate Library는 삭제하지 않고 recovery / audit 도구로 낮춰 설명하며, Operations Overview에서도 secondary tool로만 보임. |
| 5차 | 최종 Operations Console 완성 | 첫 화면에서 today action queue, primary health, archive tools, execution boundary, roadmap status를 한 번에 읽을 수 있음. |

## Scope

- Improve `Operations Overview` into an actionable Operations Console.
- Add a tested Operations audit / roadmap / action queue read model.
- Clarify Portfolio Monitoring rebalance table semantics.
- Demote archive pages by language and Overview placement without deleting routes.
- Update durable docs and root handoff logs.

## Out Of Scope

- Broker/account sync, live approval, order tickets, auto rebalance.
- Registry or saved JSONL rewrites.
- Deleting Backtest Run History or Candidate Library.
- Report export implementation.
- Moving Selected Dashboard back to Workspace / Backtest.

## Files

| File | Action | Purpose |
| --- | --- | --- |
| `tests/test_service_contracts.py` | Modify | Add TDD coverage for v2-v5 Operations Console model and rebalance semantics. |
| `app/web/operations_overview.py` | Modify | Add audit decisions, roadmap status, action queue, final console layout. |
| `app/web/final_selected_portfolio_dashboard.py` | Modify | Rename rebalance table fields and add no-order target snapshot guidance. |
| `app/web/backtest_history.py` | Modify | Strengthen archive/recovery positioning. |
| `app/web/backtest_candidate_library.py` | Modify | Strengthen archive/recovery positioning. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Modify | Document final Operations Console meaning. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Modify | Clarify rebalance target snapshot meaning. |
| `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` | Modify | Update Operations Overview responsibility. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Modify | Update Operations Console summary. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Modify | Mark V2-V5 implementation result. |
| `.aiworkspace/note/finance/WORK_PROGRESS.md` | Modify | Concise handoff. |
| `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | Modify | Record user request and decision. |

## TDD Tasks

1. Add failing tests for Operations Console roadmap / audit / action queue model.
2. Add failing test for rebalance table target snapshot semantics.
3. Implement model and UI copy changes.
4. Run focused tests and compile.
5. Browser QA on Operations Console and Portfolio Monitoring rebalance section.
6. Sync docs and commit one coherent implementation unit.
