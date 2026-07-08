# Overview Final Cleanup V33-V36 - 2026-06-29

## Goal

Close the remaining Overview refactor cleanup after V25-V32 by removing the last compatibility-heavy paths and clarifying Data Health scope.

## 이걸 하는 이유?

The Overview code was already split by tab and service domain, but four cleanup candidates still made future work harder:

- Visual renderer bodies still lived behind `app/web/overview_ui_components.py`.
- `app/web/overview_dashboard.py` still re-exported old private helper contracts.
- `app/services/overview_market_intelligence.py` still existed as an old service facade.
- `app/services/overview/data_health.py` still carried unused imports and did not separate direct Market Context data from reference / dedicated-tab data.

## Scope

1. Move Overview visual renderer bodies into `app/web/overview/components/*`.
2. Reduce `app/web/overview_dashboard.py` to a single `render_overview_dashboard` compatibility export.
3. Remove internal imports of `app.services.overview_market_intelligence` and delete that facade.
4. Clean `data_health.py` imports and add `Scope` / coverage counts for direct Market Context vs reference context targets.

## Stop Condition

- Overview component and service structure contract tests pass.
- `py_compile`, `git diff --check`, and stale path searches pass.
- Durable docs and root handoff logs are aligned.
