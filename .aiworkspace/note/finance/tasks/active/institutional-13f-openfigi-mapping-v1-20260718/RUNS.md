# Institutional 13F OpenFIGI Mapping V1 Runs

## 2026-07-18 Design Investigation

- Read finance task intake, DB pipeline, brainstorming, systematic debugging, TDD, and planning instructions.
- Read canonical finance docs and completed Institutional Portfolios context/mapping task records.
- Inspected current mapper, schema, loader joins, service guardrails, and React mapping badges.
- Queried actual DB mapping-source counts and Duquesne coverage with read-only SQL.
- Compared exact issuer joins, CUSIP-only unique candidates, ambiguous candidates, and no-candidate rows.
- Verified legacy mapping table contains CUSIP-only collisions/stale candidates that must not be promoted.
- Read official OpenFIGI API/pricing/terms and SEC ticker association documentation.
- Called OpenFIGI v3 anonymously for visible Duquesne examples, then all 68 distinct latest identifiers.
- Confirmed `ID_CUSIP`/`ID_CINS`, US Equity filtering, and one-ticker results for the actual Duquesne sample.

No implementation code or DB writes were performed during design investigation.

## 2026-07-18 Implementation Planning

- Read DB pipeline rules, data map, architecture flow, schema sync, current loader SQL, ingestion job/dispatcher/registry/section contracts, and worktree execution rules.
- Added `IMPLEMENTATION_PLAN.md` with exact TDD boundaries for five independently verifiable implementation/closeout tasks.
- Self-review aligned provider rate-header pacing, error-preserving UPSERT semantics, grouped legacy exact-name ambiguity, reverse lookup, actual DB assertions, and generated screenshot policy.

## 2026-07-18 Execution Preflight And Task 1

- Confirmed this checkout is a linked worktree on `codex/main-dev`.
- The planned `pytest` command could not start because the existing `.venv` does not contain pytest; the repository-native direct unittest run passed all 57 pre-existing Institutional Portfolios tests.
- RED: the new resolver suite failed with five `ModuleNotFoundError` errors before the module existed.
- GREEN: `tests/test_institutional_13f_mapping.py` passed 5/5 after implementing identifier normalization, US Equity jobs, safe candidate classification, provider batching, bounded retry, and proactive rate-reset pacing.
- `py_compile` and `git diff --check` passed for Task 1.

## 2026-07-18 Task 2

- RED: four persistence tests failed because the resolution table, selected-CIK reader, and conditional UPSERT did not exist.
- GREEN: the resolver/persistence suite passed 9/9 and the pre-existing Institutional Portfolios suite remained 57/57.
- Added current-state schema keyed by `(identifier_value, source)`, latest-accession selection for explicit CIKs, default missing/error retry scope, and error-preserving UPSERT semantics.
- `py_compile` and `git diff --check` passed for the schema and mapping module.
