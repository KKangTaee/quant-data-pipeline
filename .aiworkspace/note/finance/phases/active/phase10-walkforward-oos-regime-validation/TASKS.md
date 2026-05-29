# Phase 10 Walk-forward / OOS / Regime Validation Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 10-0 | `phase10-board-open` | main-dev | Phase 10 official board, roadmap sync, task split | Complete |
| 10-1 | `walkforward-oos-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Practical Validation / Robustness Lab / replay / result metadata source map and gap audit | Complete |
| 10-2 | `walkforward-split-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | walk-forward window contract and compact split evidence read model | Complete |
| 10-3 | `oos-holdout-validation-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | out-of-sample holdout evidence and in-sample-only gap treatment | Next |
| 10-4 | `regime-split-validation-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | market regime bucket evidence using DB / macro loader source | Planned |
| 10-5 | `validation-efficacy-gate-policy-refinement-v2` | `finance-backtest-web-workflow` | selected-route policy treatment for overfit / OOS / regime gaps | Planned |
| 10-6 | `phase10-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Planned |

## Immediate Next Task

`oos-holdout-validation-contract-v1`

Goal:

- 기존 normalized portfolio / benchmark curve를 사용해 in-sample / out-sample holdout evidence를 만든다.
- out-sample excess return, split deterioration, out-sample drawdown gap을 compact row로 분리한다.
- insufficient split history, missing benchmark, proxy-only evidence는 `PASS`로 처리하지 않는다.
- Walk-forward contract와 같은 저장 경계를 유지한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- historical regime split 구현
- raw split result artifact 저장
