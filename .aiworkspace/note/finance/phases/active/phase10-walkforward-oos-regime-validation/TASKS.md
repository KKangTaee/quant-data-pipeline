# Phase 10 Walk-forward / OOS / Regime Validation Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 10-0 | `phase10-board-open` | main-dev | Phase 10 official board, roadmap sync, task split | Complete |
| 10-1 | `walkforward-oos-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Practical Validation / Robustness Lab / replay / result metadata source map and gap audit | Complete |
| 10-2 | `walkforward-split-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | walk-forward window contract and compact split evidence read model | Next |
| 10-3 | `oos-holdout-validation-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | out-of-sample holdout evidence and in-sample-only gap treatment | Planned |
| 10-4 | `regime-split-validation-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | market regime bucket evidence using DB / macro loader source | Planned |
| 10-5 | `validation-efficacy-gate-policy-refinement-v2` | `finance-backtest-web-workflow` | selected-route policy treatment for overfit / OOS / regime gaps | Planned |
| 10-6 | `phase10-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Planned |

## Immediate Next Task

`walkforward-split-contract-v1`

Goal:

- 기존 normalized portfolio / benchmark curve를 사용해 compact walk-forward / rolling temporal validation contract를 만든다.
- rolling window return, benchmark return, excess return, strategy MDD, benchmark MDD, drawdown gap을 분리한다.
- missing / short / proxy-only evidence는 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- Practical Validation result payload에는 compact audit evidence만 연결하고 raw split artifact는 저장하지 않는다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- OOS holdout row 전체 구현
- historical regime split 구현
- raw split result artifact 저장
