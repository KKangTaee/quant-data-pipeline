# Overview Legacy Cleanup V6-V10 Risks

- `legacy_dashboard.py` still exports many compatibility names through `overview_dashboard.py`; deletion must be based on direct active-path usage plus contract coverage, not name appearance alone.
- `overview_market_intelligence.py` is large and tested directly in `OverviewMarketIntelligenceServiceContractTests`; V8 should move only bounded read-model helpers with focused tests.
- V9 removed only confirmed unused standalone wrappers and Candidate Ops overview snapshot helpers. The remaining `legacy_dashboard.py` helper cluster is still large because active tab modules call it for controls, charts, refresh bars, and action wiring; V10 should guard the boundary rather than deleting broad helper groups.
