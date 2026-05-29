# Phase 12 Selected Monitoring / Recheck Operations Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 12-0 | `phase12-board-open` | main-dev | Phase 12 official board, roadmap sync, task split | Complete |
| 12-1 | `selected-monitoring-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Selected Dashboard / Final Review / runtime monitoring evidence source map and gap audit | Complete |
| 12-2 | `recheck-readiness-freshness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | DB market freshness, benchmark / component replay contract, missing / stale readiness policy | Complete |
| 12-3 | `selected-provider-evidence-staleness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | provider holdings / exposure / operability freshness and coverage policy for selected portfolios | Complete |
| 12-4 | `recheck-comparison-review-signal-policy-v1` | `finance-backtest-web-workflow` | recheck baseline deterioration, review signal severity, failed / missing recheck handling | Next |
| 12-5 | `allocation-drift-evidence-boundary-v1` | `finance-backtest-web-workflow` | optional actual allocation / drift evidence read-only boundary and alert preview | Pending |
| 12-6 | `decision-dossier-continuity-operations-v1` | `finance-backtest-web-workflow` | selected decision dossier / continuity / timeline operations evidence consistency | Pending |
| 12-7 | `phase12-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, storage boundary, phase closeout | Pending |

## Next Target

`recheck-comparison-review-signal-policy-v1`

Goal:

- Recheck Comparison을 Review Signals의 policy owner로 삼아 CAGR / MDD / benchmark spread threshold 중복을 제거한다.
- missing / failed / partial recheck가 `Clear`처럼 보이지 않게 한다.
- Provider Evidence, Recheck Preflight, Recheck Comparison의 route가 monitoring signal로 일관되게 이어지게 한다.

Out of scope:

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- broker order / live approval / auto rebalance
- account holdings 자동 연결
- UI direct provider / FRED / broker fetch
- full holdings / price history / macro series workflow JSONL 저장
