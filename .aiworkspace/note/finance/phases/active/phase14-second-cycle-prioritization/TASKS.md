# Phase 14 Second-Cycle Prioritization Tasks

Status: Active
Created: 2026-05-30

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 14-0 | `phase14-board-open` | main-dev | Phase 14 official board, scope, task split, immediate next task | Complete |
| 14-1 | `phase14-candidate-prioritization-v1` | `finance-task-intake` + `finance-integration-review` | rank Phase 13 carry-forward candidates and select first implementation slice | Next |
| 14-2 | `phase14-first-slice-design-v1` | matching domain skill after 14-1 | define first implementation files, contracts, tests, storage boundary | Pending |
| 14-3 | `phase14-handoff-closeout` | `finance-integration-review` + `finance-doc-sync` | close prioritization phase and hand off selected implementation task / phase | Pending |

## Next Target

`phase14-candidate-prioritization-v1`

Goal:

- Use `phase13-residual-risk-carry-forward-v1/CARRY_FORWARD_MATRIX.md` as the input.
- Rank high-priority candidates by impact, dependency readiness, implementation effort, source uncertainty, storage boundary risk, and QA coverage.
- Recommend the first implementation slice without opening code changes inside the prioritization task.

Out of scope:

- code implementation
- new JSONL registry
- user memo / preset persistence
- monitoring log automatic append
- broker order / live approval / account sync / auto rebalance
- paid or approval-based data source adoption
