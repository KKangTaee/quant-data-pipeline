# Lifecycle Audit Scoring V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 8에서 lifecycle evidence source가 늘어났다.
이제 Data Coverage Audit은 단순히 lifecycle row가 있는지보다, 어떤 row가 actual coverage이고 어떤 row가 partial current snapshot / SEC identity / computed partial인지 분리해 보여줘야 한다.

## Scope

포함한다.

- Data Coverage Audit의 lifecycle evidence 분류를 source semantics 기준으로 보강한다.
- current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting evidence를 compact metrics로 분리한다.
- Universe / listing evidence와 Survivorship / delisting control row가 partial evidence의 이유를 더 구체적으로 표시하게 한다.
- service contract test를 추가한다.
- Phase 8 board / docs / roadmap / root log를 동기화한다.

포함하지 않는다.

- 새 DB table / schema
- 새 ingestion collector
- 새 JSONL registry
- user memo / preset persistence
- UI direct fetch
- live approval / broker order / auto rebalance

## Done Criteria

- partial snapshot / SEC identity / computed partial evidence가 PASS로 승격되지 않는다.
- actual requested-period coverage만 survivorship PASS를 만든다.
- audit metrics가 source별 symbol lists와 row counts를 포함한다.
- compile, focused tests, full service contracts, `git diff --check`가 통과한다.
