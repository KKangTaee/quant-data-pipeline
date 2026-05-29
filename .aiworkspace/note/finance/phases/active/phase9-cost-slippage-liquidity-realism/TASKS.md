# Phase 9 Cost / Slippage / Liquidity Realism Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 9-0 | `phase9-board-open` | main-dev | Phase 9 official board, roadmap sync, task split | Complete |
| 9-1 | `cost-model-source-contract-review-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | current runtime / validation cost metadata source map and gap review | Complete |
| 9-2 | `turnover-rebalance-evidence-v1` | `finance-strategy-implementation` + `finance-backtest-web-workflow` | turnover / rebalance cadence evidence contract and audit read model | Complete |
| 9-3 | `net-cost-curve-application-v1` | `finance-strategy-implementation` | prove when transaction cost is actually reflected in net result curve | Pending |
| 9-4 | `liquidity-capacity-evidence-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | DB provider / price based liquidity and capacity evidence refinement | Pending |
| 9-5 | `cost-slippage-sensitivity-audit-v1` | `finance-backtest-web-workflow` | read-only cost / slippage sensitivity rows in Backtest Realism Audit | Pending |
| 9-6 | `backtest-realism-gate-policy-refinement-v1` | `finance-backtest-web-workflow` | selected-route policy treatment for cost / liquidity gaps | Pending |
| 9-7 | `phase9-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Pending |

## Immediate Next Task

`net-cost-curve-application-v1`

Goal:

- cost application proof와 turnover evidence가 실제 net result curve 해석에 어떻게 연결되는지 확인한다.
- gross / net / estimated cost columns and metadata가 Final Review / Backtest Realism Audit에서 일관되게 읽히는지 보강한다.
- cost application proof가 없는 legacy source를 과대 평가하지 않도록 한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- full execution simulator
