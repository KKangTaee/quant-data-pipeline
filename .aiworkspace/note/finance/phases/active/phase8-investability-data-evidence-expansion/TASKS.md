# Phase 8 Investability Data Evidence Expansion Tasks

Status: Active
Created: 2026-05-28

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 8-0 | `phase8-board-open` | main-dev | Phase 8 official board, roadmap sync, carry-forward mapping | Complete |
| 8-1 | `symbol-lifecycle-event-fields-v1` | `finance-db-pipeline` | lifecycle schema event fields, Form 25 / current listing row contract, loader/test/docs | Implementation complete |
| 8-2 | `historical-membership-source-review-v1` | main-dev + `finance-db-pipeline` | free / official source 후보 조사, source contract, ingestion feasibility | Complete |
| 8-3 | `symbol-directory-snapshot-ingestion-v1` | `finance-db-pipeline` | Nasdaq public current symbol directory files를 lifecycle `listing_observed` evidence로 적재 | Pending |
| 8-4 | `sec-cik-exchange-crosscheck-v1` | `finance-db-pipeline` | SEC current CIK / ticker / exchange association을 lifecycle evidence 보조 source로 연결 | Pending |
| 8-5 | `computed-snapshot-lifecycle-v1` | `finance-db-pipeline` + `finance-backtest-web-workflow` | repeated current snapshots 기반 computed lifecycle evidence 설계 / scoring | Pending |
| 8-6 | `lifecycle-audit-scoring-v1` | `finance-backtest-web-workflow` | Data Coverage Audit evidence scoring refinement | Pending |
| 8-7 | `phase8-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Pending |

## Previous Work Folded Into Phase 8

아래 task는 Phase 8 공식 오픈 전에 이미 완료됐지만 Phase 8의 선행 기반으로 본다.

- `historical-universe-survivorship-v1`
- `sec-form25-delisting-backfill-v1`
- `sec-form25-ingestion-ui-v1`

## Immediate Next Task

`symbol-directory-snapshot-ingestion-v1`

Goal:

- Nasdaq public current symbol directory files를 DB lifecycle evidence로 적재한다.
- current listing row는 `current_listing_snapshot` / `listing_observed` / `partial`로 저장한다.
- survivorship PASS 기준은 완화하지 않는다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- UI direct fetch
- live approval / broker order / auto rebalance

## Source Review Decision

`historical-membership-source-review-v1` 결과:

- Nasdaq Daily List는 corporate action source로 가장 강하지만 subscription / approval product이므로 Phase 8 free-source-first 구현 대상에서 제외한다.
- Nasdaq public Symbol Directory current files는 바로 접근 가능하고 current listing snapshot evidence로 적합하다.
- SEC ticker / exchange files와 Submissions API는 CIK / entity continuity 보조 source로 사용하되 complete historical membership으로 보지 않는다.
