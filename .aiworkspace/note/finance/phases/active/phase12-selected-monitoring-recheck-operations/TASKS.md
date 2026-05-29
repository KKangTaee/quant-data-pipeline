# Phase 12 Selected Monitoring / Recheck Operations Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 12-0 | `phase12-board-open` | main-dev | Phase 12 official board, roadmap sync, task split | Complete |
| 12-1 | `selected-monitoring-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Selected Dashboard / Final Review / runtime monitoring evidence source map and gap audit | Complete |
| 12-2 | `recheck-readiness-freshness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | DB market freshness, benchmark / component replay contract, missing / stale readiness policy | Complete |
| 12-3 | `selected-provider-evidence-staleness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | provider holdings / exposure / operability freshness and coverage policy for selected portfolios | Next |
| 12-4 | `recheck-comparison-review-signal-policy-v1` | `finance-backtest-web-workflow` | recheck baseline deterioration, review signal severity, failed / missing recheck handling | Pending |
| 12-5 | `allocation-drift-evidence-boundary-v1` | `finance-backtest-web-workflow` | optional actual allocation / drift evidence read-only boundary and alert preview | Pending |
| 12-6 | `decision-dossier-continuity-operations-v1` | `finance-backtest-web-workflow` | selected decision dossier / continuity / timeline operations evidence consistency | Pending |
| 12-7 | `phase12-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, storage boundary, phase closeout | Pending |

## Next Target

`selected-provider-evidence-staleness-contract-v1`

Goal:

- Selected Portfolio Dashboard의 Provider Evidence가 selected component ticker weight 기준 provider holdings / exposure / operability freshness와 coverage를 일관된 contract로 표시하게 한다.
- stale provider snapshot, partial coverage, missing holdings / exposure, fallback symbol source가 pass처럼 보이지 않게 한다.
- provider collection은 UI에서 직접 실행하지 않고 기존 Ingestion -> DB -> Loader 경계를 유지한다.

Out of scope:

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- broker order / live approval / auto rebalance
- account holdings 자동 연결
- UI direct provider / FRED / broker fetch
- full holdings / price history / macro series workflow JSONL 저장
