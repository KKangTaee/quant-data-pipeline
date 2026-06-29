# Overview IA Cleanup V22 Risks

- `app/web/overview_dashboard_helpers.py` still contains candidate snapshot helper functions used by the former Candidate Ops surface. They are not rendered by Overview after V22, but the helper code is retained until a separate Backtest / Operations audit decides whether to move or delete it.
- `build_overview_data_health_ingestion_handoff()` remains as a service helper and historical task artifact. Current Overview top-level UI no longer renders it directly; Market Context source confidence and Operations / Ingestion own the practical data-health path.
- Sector / Industry still has internal `Heatmap / Line / Latest Delta` chart tabs for trend detail. V22 only removes the extra top-level `Trend / Table` split and demotes raw tables.
