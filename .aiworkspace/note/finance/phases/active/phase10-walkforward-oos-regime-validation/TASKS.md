# Phase 10 Walk-forward / OOS / Regime Validation Tasks

Status: Complete
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 10-0 | `phase10-board-open` | main-dev | Phase 10 official board, roadmap sync, task split | Complete |
| 10-1 | `walkforward-oos-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Practical Validation / Robustness Lab / replay / result metadata source map and gap audit | Complete |
| 10-2 | `walkforward-split-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | walk-forward window contract and compact split evidence read model | Complete |
| 10-3 | `oos-holdout-validation-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | out-of-sample holdout evidence and in-sample-only gap treatment | Complete |
| 10-4 | `regime-split-validation-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | market regime bucket evidence using DB / macro loader source | Complete |
| 10-5 | `validation-efficacy-gate-policy-refinement-v2` | `finance-backtest-web-workflow` | selected-route policy treatment for overfit / OOS / regime gaps | Complete |
| 10-6 | `phase10-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Complete |

## Immediate Next Task

`phase11-board-open`

Goal:

- Phase 11 portfolio construction risk controls의 official board를 연다.
- concentration, overlap, correlation, risk contribution, component role / weight discipline 범위를 정리한다.
- Phase 10 검증 효력 gate 이후 portfolio construction 단계에서 무엇을 막아야 하는지 task로 분해한다.
- 새 저장 기능 없이 phase board와 source map부터 시작한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- live trading signal generation
- waiver UI / persistence
- raw validation artifact 저장
