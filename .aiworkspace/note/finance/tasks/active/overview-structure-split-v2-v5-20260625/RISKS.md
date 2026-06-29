# Overview Structure Split V2-V5 Risks

- Legacy helper internals remain large. The safe strategy is to move active ownership boundaries first, then retire legacy helpers only when tests no longer depend on them.
- After V2, tab modules own orchestration but still call many `legacy_dashboard.py` helpers. V3/V4 should reduce those dependencies through component and service import surfaces before deleting helper code.
- After V3, component domain modules are import surfaces over `overview_ui_components.py`; they do not yet physically move the full renderer implementations.
- After V4, service domain modules are import surfaces over `overview_market_intelligence.py`; they do not yet physically split the full market intelligence calculation body.
- After V5, tests guard the new import boundaries, but the next cleanup still needs deliberate physical extraction from `legacy_dashboard.py` / `overview_market_intelligence.py` before those monoliths can be retired.
