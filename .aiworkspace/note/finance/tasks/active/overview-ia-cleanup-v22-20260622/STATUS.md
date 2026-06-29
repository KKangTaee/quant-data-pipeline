# Overview IA Cleanup V22 Status

Status: Complete

## 진행

- RED tests added for Overview primary tab selector, Data Health demotion, Candidate Ops removal, IA guide update, and Sector / Industry summary-first table handling.
- Overview primary tab selector now keeps only `Market Context`, `Market Movers`, `Futures Monitor`, `Sentiment`, `Sector / Industry`, and `Events`.
- `Data Health` and `Candidate Ops` render paths were removed from `app/web/overview_dashboard.py`.
- `Sector / Industry` keeps summary / chart-first flow and moves raw tables under `상세 표`.
- `load_overview_ia_closeout_model()` now treats Data Repair as an external Operations / Ingestion owner and no longer includes Candidate Ops.

## 완료

- Full service contract test run passed.
- Browser QA passed with screenshot `overview-ia-cleanup-v22-qa.png`.
- Documentation closeout updated INDEX, ROADMAP, PROJECT_MAP, flow map, runbook, manifest, and root handoff logs.
