# Phase 9 Cost / Slippage / Liquidity Realism Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 9-0 | `phase9-board-open` | main-dev | Phase 9 official board, roadmap sync, task split | Complete |
| 9-1 | `cost-model-source-contract-review-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | current runtime / validation cost metadata source map and gap review | Complete |
| 9-2 | `turnover-rebalance-evidence-v1` | `finance-strategy-implementation` + `finance-backtest-web-workflow` | turnover / rebalance cadence evidence contract and audit read model | Complete |
| 9-3 | `net-cost-curve-application-v1` | `finance-strategy-implementation` | prove when transaction cost is actually reflected in net result curve | Complete |
| 9-4 | `liquidity-capacity-evidence-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | DB provider / price based liquidity and capacity evidence refinement | Complete |
| 9-5 | `cost-slippage-sensitivity-audit-v1` | `finance-backtest-web-workflow` | read-only cost / slippage sensitivity rows in Backtest Realism Audit | Complete |
| 9-6 | `backtest-realism-gate-policy-refinement-v1` | `finance-backtest-web-workflow` | selected-route policy treatment for cost / liquidity gaps | Complete |
| 9-7 | `phase9-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Pending |

## Immediate Next Task

`phase9-integrated-qa-closeout`

Goal:

- Phase 9 전체 cost / slippage / turnover / liquidity realism 변경을 통합 검증한다.
- Backtest Realism Audit, Final Review gate policy, docs, storage boundary를 마지막으로 점검한다.
- 1차 hardening cycle 다음 Phase 10 handoff에 필요한 남은 risk와 follow-up을 정리한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- full execution simulator
- market impact simulator
