# Phase 12 Selected Monitoring / Recheck Operations Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 12-0 | `phase12-board-open` | main-dev | Phase 12 official board, roadmap sync, task split | Complete |
| 12-1 | `selected-monitoring-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Selected Dashboard / Final Review / runtime monitoring evidence source map and gap audit | Complete |
| 12-2 | `recheck-readiness-freshness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | DB market freshness, benchmark / component replay contract, missing / stale readiness policy | Next |
| 12-3 | `selected-provider-evidence-staleness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | provider holdings / exposure / operability freshness and coverage policy for selected portfolios | Pending |
| 12-4 | `recheck-comparison-review-signal-policy-v1` | `finance-backtest-web-workflow` | recheck baseline deterioration, review signal severity, failed / missing recheck handling | Pending |
| 12-5 | `allocation-drift-evidence-boundary-v1` | `finance-backtest-web-workflow` | optional actual allocation / drift evidence read-only boundary and alert preview | Pending |
| 12-6 | `decision-dossier-continuity-operations-v1` | `finance-backtest-web-workflow` | selected decision dossier / continuity / timeline operations evidence consistency | Pending |
| 12-7 | `phase12-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, storage boundary, phase closeout | Pending |

## Next Target

`recheck-readiness-freshness-contract-v1`

Goal:

- Final Review V2 selected row, embedded component contract 후보, Current Candidate Registry fallback, DB latest market date, symbol freshness를 하나의 operations preflight contract로 정리한다.
- Performance Recheck를 실행하기 전에 missing replay contract, stale / missing price, missing benchmark price, DB latest market date error가 pass처럼 보이지 않게 한다.
- 기존 DB loader / registry read boundary를 유지하고 새 persistence 없이 구현한다.

Out of scope:

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- broker order / live approval / auto rebalance
- account holdings 자동 연결
- UI direct provider / FRED / broker fetch
- full holdings / price history / macro series workflow JSONL 저장
