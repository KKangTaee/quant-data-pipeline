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
| 5 | `look-through-exposure-board-v1` | `finance-db-pipeline` + `finance-backtest-web-workflow` | holdings / exposure coverage board and Final Review summary | Implementation complete |
| 6 | `robustness-lab-v1` | `finance-strategy-implementation` + backtest workflow | walk-forward / sensitivity / stress evidence surface | Implementation complete |
| 7 | `selected-monitoring-timeline-v1` | `finance-backtest-web-workflow` | selected portfolio review signals over time without auto-save sprawl | Planned |
| 8 | `decision-dossier-report-v1` | backtest workflow + doc sync | human-readable final decision dossier / export contract | Planned |

## Immediate Next Task

Next recommended implementation task is `selected-monitoring-timeline-v1`.

Goal:

- `selected-monitoring-timeline-v1`: selected portfolio 상태 변화를 자동 저장 없이 review signal timeline으로 읽는다.

Expected files:

- selected monitoring timeline: `app/runtime/final_selected_portfolios.py`, `app/web/final_selected_portfolio_dashboard*.py`, selected monitoring docs/flows.

Out of scope for the next task:

- new JSONL registry
- registry rewrite
- user memo storage

## Dependency Notes

- Task 2 should land before report or monitoring work so downstream screens can rely on a stable gate contract.
- Task 3 completed as documentation / audit only; it did not rewrite registries.
- Task 4 implemented compact source / freshness fields without adding storage.
- Task 5 implemented a compact look-through board inside provider context; full holdings / exposure rows remain DB-only.
- Task 6 implemented a compact robustness board from existing stress / rolling / sensitivity / overfit evidence without adding a new registry.
- Task 7 should avoid automatic monitoring log writes. Monitoring snapshots should be explicit user action unless a later automation policy is approved.

## Completion Standard Per Task

Every implementation task should include:

- active task docs with `이걸 하는 이유?`
- service-level contract tests when logic is Streamlit-free
- `git diff --check`
- relevant `py_compile` or unit tests
- UI smoke with Browser when visible Streamlit behavior changes
- docs / roadmap sync only for durable workflow changes
