# Backtest Factor Readiness Panel V1 Status

Status: In Progress
Started: 2026-07-07

## Current Step

- 4차 완료: strict annual Quality / Value / Quality + Value Single Strategy forms are limited to a five-year backtest window.

## Completed

- Created `build_strict_factor_readiness_panel_model` in `app/web/backtest_common.py`.
- Added focused service contracts for mixed issue and ready states.
- Added UI-only `backtest_factor_readiness_panel` React component and build asset.
- Added `_render_strict_factor_readiness_panel` to combine price freshness and statement shadow coverage for strict annual factor setup.
- Replaced the old price-only preflight call in Single Strategy Quality, Value, and Quality + Value strict annual forms.
- Added shared five-year strict factor window helpers and submit-time validation.
- Changed Single Strategy strict annual factor defaults from 2016-01-01 to the latest allowed five-year start date.
