# Phase 8 Investability Data Evidence Expansion Integration

Status: Active
Created: 2026-05-28

## Integration Boundaries

| Area | Files | Risk |
| --- | --- | --- |
| DB schema | `finance/data/db/schema.py` | Adds nullable event fields to existing table |
| Current listing ingestion | `finance/data/nyse_db.py` | Must keep current snapshot partial |
| Computed lifecycle ingestion | `finance/data/computed_lifecycle.py`, `app/jobs/ingestion_jobs.py` | Must keep repeated snapshot evidence partial unless a future source contract can mark actual |
| SEC Form 25 ingestion | `finance/data/sec_delisting.py` | Must keep delisting-only semantics |
| Loader | `finance/loaders/universe.py` | Must remain read-only compact summary |
| Data Coverage Audit | `app/services/backtest_data_coverage_audit.py` | Source-specific lifecycle scoring must not loosen selected-route policy |
| Tests | `tests/test_service_contracts.py` | Contract should prove no JSONL / memo side effects |
| Docs | `docs/data/*`, `docs/architecture/*`, `docs/ROADMAP.md` | Must distinguish implemented behavior from future source work |

## Verification Plan

- `git diff --check`
- `python -m py_compile finance/data/db/schema.py finance/data/nyse_db.py finance/data/sec_delisting.py finance/data/computed_lifecycle.py finance/loaders/universe.py app/services/backtest_data_coverage_audit.py`
- focused service contracts around lifecycle / Form 25 / Data Coverage Audit scoring
- docs status review
