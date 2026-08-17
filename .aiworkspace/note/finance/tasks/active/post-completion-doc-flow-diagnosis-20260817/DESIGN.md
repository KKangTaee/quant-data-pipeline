# Design

## Diagnostic Axes

- Product surface: `app/web/streamlit_app.py` top navigation and each page route.
- Market Research subviews: `app/web/overview/navigation.py` current 3-family / 8-view contract.
- Durable docs: `docs/INDEX.md`, `PRODUCT_DIRECTION.md`, `ROADMAP.md`, `PROJECT_MAP.md`, focused architecture / flow / data / runbook docs.
- Workflow state: task / phase manifests and normalized `State:`.
- Drift scan: old `Workspace > Overview`, `Workspace > Ingestion`, `Operations > Portfolio Monitoring`, `Selected Portfolio Dashboard`, `Futures Monitor`, `Sector / Industry`, `Data Health`, old Reference Guides / Glossary terms.

## Classification

- Must fix: current canonical docs would send a worker to an old route, wrong owner, wrong source-of-truth, or wrong state.
- Candidate cleanup: retained history or glossary text is noisy but not harmful to current docs.
- Intentional retained history: old task records, legacy file names, compatibility labels, or saved JSONL names that should remain.
