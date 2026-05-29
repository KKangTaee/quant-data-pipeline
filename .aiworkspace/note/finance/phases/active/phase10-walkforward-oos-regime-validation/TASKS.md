# Phase 10 Walk-forward / OOS / Regime Validation Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 10-0 | `phase10-board-open` | main-dev | Phase 10 official board, roadmap sync, task split | Complete |
| 10-1 | `walkforward-oos-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Practical Validation / Robustness Lab / replay / result metadata source map and gap audit | Next |
| 10-2 | `walkforward-split-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | walk-forward window contract and compact split evidence read model | Planned |
| 10-3 | `oos-holdout-validation-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | out-of-sample holdout evidence and in-sample-only gap treatment | Planned |
| 10-4 | `regime-split-validation-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | market regime bucket evidence using DB / macro loader source | Planned |
| 10-5 | `validation-efficacy-gate-policy-refinement-v2` | `finance-backtest-web-workflow` | selected-route policy treatment for overfit / OOS / regime gaps | Planned |
| 10-6 | `phase10-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Planned |

## Immediate Next Task

`walkforward-oos-source-map-v1`

Goal:

- 현재 Practical Validation, Robustness Lab, Validation Efficacy Audit, Final Review gate가 어떤 curve / benchmark / macro / replay evidence를 읽는지 확인한다.
- walk-forward, OOS holdout, regime split에 재사용 가능한 helper와 부족한 source를 분리한다.
- 코드 변경이 필요한 파일과 test scope를 확정한다.
- 저장 경계상 새 JSONL / memo / preset 저장 없이 가능한 구현 경로를 먼저 선택한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- paid source 우선 도입
- full ML optimizer
- raw split result artifact 저장
