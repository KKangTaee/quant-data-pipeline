# Runs

## 2026-07-17 Baseline

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`
- Branch: `codex/sub-dev`
- Starting commit: `e7702ac4`
- Command: `PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py -q`
- Result: `35 passed`, with three pre-existing edgar deprecation warnings.

## 2026-07-17 Implementation

- TDD commits: `22c2b4bd`, `e28b4d97`, `92960ec5`, `235e3eda`, `2ec32829`, `4f58fbcc`.
- FRED refresh: requested 5 series, stored 6,698 rows, missing `[]`, failed `[]` for the recent 5 years 4 months.
- Focused verification: `48 passed`, with three pre-existing edgar deprecation warnings.
- React: `npm run build` completed; Vite transformed 170 modules and rebuilt `component_static`.
- Actual read model: schema `economic_cycle_v2`, gold `SUFFICIENT`, dollar `PARTIAL`; no provider calls occur in the UI path.
- Browser QA: desktop two-column and 420px one-column overflow `0`; white uniform pathway borders, focus detail opacity `1`, mobile details open with 5d/date/freshness, clean-tab console errors `0`.
- QA screenshot: `/Users/taeho/.codex/qa/economic-cycle-multichannel-desktop-20260717.png` (generated, not committed).
