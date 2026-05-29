# Phase 10 Walk-forward / OOS / Regime Validation Tasks

Status: Active
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
| 10-6 | `phase10-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Next |

## Immediate Next Task

`phase10-integrated-qa-closeout`

Goal:

- Phase 10의 temporal / OOS / regime / Validation Efficacy / Final Review gate 변경을 통합 검증한다.
- service contract, compile, UI-engine boundary, finance refinement hygiene를 실행한다.
- Phase 10 완료 요약과 다음 hardening target을 정리한다.
- 새 저장 기능 없이 구현 / 문서 / 검증 상태만 closeout한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- live trading signal generation
- waiver UI / persistence
- raw validation artifact 저장
