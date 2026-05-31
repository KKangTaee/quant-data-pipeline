# Investability Decision Foundation Tasks

Status: Implementation Complete
Created: 2026-05-28

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 0 | `investability-decision-foundation-phase0` | main-dev | phase policy, task graph, roadmap sync | Complete |
| 1 | `investability-evidence-packet-v1` | `finance-backtest-web-workflow` | Final Review packet / selected route gate / compact snapshot | Implementation complete |
| 2 | `validation-gate-hardening-v1` | `finance-backtest-web-workflow` | critical diagnostic matrix, route policy, optional waiver design | Implementation complete |
| 3 | `storage-governance-audit-v1` | main-dev + doc sync | existing JSONL writes review and keep/remove policy | Complete |
| 4 | `data-provenance-coverage-v1` | `finance-db-pipeline` | source provenance fields, freshness / coverage read model, free-source-first contracts | Implementation complete |
| 5 | `look-through-exposure-board-v1` | `finance-db-pipeline` + `finance-backtest-web-workflow` | holdings / exposure coverage board and Final Review summary | Implementation complete |
| 6 | `robustness-lab-v1` | `finance-strategy-implementation` + backtest workflow | walk-forward / sensitivity / stress evidence surface | Implementation complete |
| 7 | `selected-monitoring-timeline-v1` | `finance-backtest-web-workflow` | selected portfolio review signals over time without auto-save sprawl | Implementation complete |
| 8 | `decision-dossier-report-v1` | backtest workflow + doc sync | human-readable final decision dossier / export contract | Implementation complete |

## Immediate Next Task

Next recommended step is a separate structured waiver policy decision or Practical Validation V2 P2 closeout.

Goal:

- `structured-waiver-policy-v1`: critical gap waiver를 허용할지, 허용한다면 expiry / scope / review trigger를 어떻게 제한할지 결정한다.
- `practical-validation-v2-p2-closeout`: provider / macro / stress evidence 정상화가 P2 기준을 충족했는지 확인한다.

Expected files:

- structured waiver: `app/services/backtest_evidence_read_model.py`, `app/web/backtest_final_review*.py`, docs/flows, tests.
- P2 closeout: `.aiworkspace/note/finance/tasks/active/practical-validation-v2/`, docs/data, docs/flows.

Out of scope for the next task:

- new JSONL registry
- registry rewrite
- user memo storage
- live approval / broker order / auto rebalance

## Dependency Notes

- Task 2 should land before report or monitoring work so downstream screens can rely on a stable gate contract.
- Task 3 completed as documentation / audit only; it did not rewrite registries.
- Task 4 implemented compact source / freshness fields without adding storage.
- Task 5 implemented a compact look-through board inside provider context; full holdings / exposure rows remain DB-only.
- Task 6 implemented a compact robustness board from existing stress / rolling / sensitivity / overfit evidence without adding a new registry.
- Task 7 implemented a read-only Timeline tab and did not add automatic monitoring log writes. Monitoring snapshots should stay explicit user action unless a later automation policy is approved.
- Task 8 implemented a read-only markdown dossier export without automatic report file writes.
- Closeout recorded this phase as implementation complete. Follow-up work should open a new task instead of extending this board.

## Completion Standard Per Task

Every implementation task should include:

- active task docs with `이걸 하는 이유?`
- service-level contract tests when logic is Streamlit-free
- `git diff --check`
- relevant `py_compile` or unit tests
- UI smoke with Browser when visible Streamlit behavior changes
- docs / roadmap sync only for durable workflow changes
