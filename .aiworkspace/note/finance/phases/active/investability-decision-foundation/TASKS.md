# Investability Decision Foundation Tasks

Status: Active
Created: 2026-05-28

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 0 | `investability-decision-foundation-phase0` | main-dev | phase policy, task graph, roadmap sync | Complete |
| 1 | `investability-evidence-packet-v1` | `finance-backtest-web-workflow` | Final Review packet / selected route gate / compact snapshot | Implementation complete |
| 2 | `validation-gate-hardening-v1` | `finance-backtest-web-workflow` | critical diagnostic matrix, route policy, optional waiver design | Implementation complete |
| 3 | `storage-governance-audit-v1` | main-dev + doc sync | existing JSONL writes review and keep/remove policy | Complete |
| 4 | `data-provenance-coverage-v1` | `finance-db-pipeline` | source provenance fields, freshness / coverage read model, free-source-first contracts | Implementation complete |
| 5 | `look-through-exposure-board-v1` | `finance-db-pipeline` + `finance-backtest-web-workflow` | holdings / exposure coverage board and Final Review summary | Planned |
| 6 | `robustness-lab-v1` | `finance-strategy-implementation` + backtest workflow | walk-forward / sensitivity / stress evidence surface | Planned |
| 7 | `selected-monitoring-timeline-v1` | `finance-backtest-web-workflow` | selected portfolio review signals over time without auto-save sprawl | Planned |
| 8 | `decision-dossier-report-v1` | backtest workflow + doc sync | human-readable final decision dossier / export contract | Planned |

## Immediate Next Task

Next recommended implementation task is `look-through-exposure-board-v1`.

Goal:

- `look-through-exposure-board-v1`: holdings / exposure coverage board and Final Review summary using the compact provenance baseline.

Expected files:

- look-through board: `finance/loaders/provider.py`, `app/services/backtest_practical_validation_provider_context.py`, Practical Validation / Final Review display, docs/data.

Out of scope for the next task:

- new JSONL registry
- registry rewrite
- user memo storage

## Dependency Notes

- Task 2 should land before report or monitoring work so downstream screens can rely on a stable gate contract.
- Task 3 completed as documentation / audit only; it did not rewrite registries.
- Task 4 implemented compact source / freshness fields without adding storage.
- Task 5 can now build on the provenance contract instead of inventing another persistence layer.
- Task 6 should use existing strategy runtime / proven libraries where possible; avoid hand-rolled simulation if a reliable local implementation exists.
- Task 7 should avoid automatic monitoring log writes. Monitoring snapshots should be explicit user action unless a later automation policy is approved.

## Completion Standard Per Task

Every implementation task should include:

- active task docs with `이걸 하는 이유?`
- service-level contract tests when logic is Streamlit-free
- `git diff --check`
- relevant `py_compile` or unit tests
- UI smoke with Browser when visible Streamlit behavior changes
- docs / roadmap sync only for durable workflow changes
