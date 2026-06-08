# Overview Data Health Ingestion Handoff V1 Design

Status: Active
Created: 2026-06-08

## Design

The service layer adds a Streamlit-free handoff model derived only from the existing `build_collection_ops_snapshot` output.
It ranks non-OK rows by severity and freshness risk, then maps each collection area to a user-facing target surface and collection lane.

The UI renders this model at the top of `Workspace > Overview > Data Health`.
The lane should make the next operator step obvious without making Overview own ingestion execution.

## Components

| Component | Responsibility |
| --- | --- |
| `app/services/overview_market_intelligence.py` | Build handoff summary, priority rows, status counts, target surface mapping, boundary note |
| `app/web/overview_dashboard_helpers.py` | Load handoff model from the same cached DB/run-history snapshot path |
| `app/web/overview_ui_components.py` | Render compact handoff lane/cards with source/freshness visible |
| `app/web/overview_dashboard.py` | Place handoff lane before raw Data Health status cards/table |
| `tests/test_service_contracts.py` | Guard ranking, surface mapping, boundary, and render ordering |

## Boundary

The handoff model is read-only.
It does not call `app/jobs/ingestion_jobs.py`, write registry/saved JSONL, change schema, or fetch providers during render.
If a collection is needed, the user is pointed to existing `Workspace > Ingestion` or approved Overview action surfaces.
