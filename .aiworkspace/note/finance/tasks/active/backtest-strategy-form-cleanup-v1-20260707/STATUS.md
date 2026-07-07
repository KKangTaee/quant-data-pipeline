# Backtest Strategy Form Cleanup V1 Status

Status: Done
Started: 2026-07-07

## Why

The previous Strategy Detail React panel over-interpreted the request. The intended improvement is to keep the existing strategy selector and form switching, then clean the per-strategy form surfaces, especially strict Quality / Value preset and preflight areas.

## Roadmap

1. Remove the active Strategy Detail panel and stale active contracts.
2. Clean strict preset helper copy and model.
3. Clean Quality / Value strict Single Strategy forms.
4. Check Equal Weight / ETF-like strategy forms.
5. Check Portfolio Mix Builder impact and sync docs.

## Current

- 2026-07-07: task opened after user clarified the intended UX scope.
- 2026-07-07: 1차 removed the overbuilt active Strategy Detail panel and stale panel artifacts while keeping Price Freshness Preflight.
- 2026-07-07: 2차 added compact strict preset display model and renderer copy for current basis / caveat / update path.
- 2026-07-07: 3차 cleaned strict annual / quarterly Single Strategy form guidance and Browser QA confirmed Quality / Value strict flows.
- 2026-07-07: 4차 kept ETF-like strategy forms as Streamlit form-first flows, removed confusing runtime-wrapper copy, and Browser QA confirmed Equal Weight / GTAA switching.
- 2026-07-07: 5차 confirmed Portfolio Mix Builder remains Streamlit-owned, renders Quality strict settings with compact preset basis, synced durable docs, and closed the task.
