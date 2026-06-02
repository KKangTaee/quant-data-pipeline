# Futures Monitor UI V2 Runs

## 2026-06-02

- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py` - PASS.
- `git diff --check` - PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS.
- `uv run python -m unittest tests.test_service_contracts` - PASS, 234 tests.
- Browser QA on `http://localhost:8517/`:
  - PASS: `Futures Workspace`, `Data Feed`, `Macro Context`, `Live Futures Charts`, `Diagnostics & Provider Evidence` rendered.
  - PASS: old body peer tabs `Shock Board`, `Candles`, `Provider Run` not present.
  - QA screenshot saved as generated artifact: `futures-monitor-ui-v2-qa.png`.

## 2026-06-02 V2.1 follow-up

- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py` - PASS.
- `git diff --check` - PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS.
- `uv run python -m unittest tests.test_service_contracts` - PASS, 234 tests.
- Browser QA on `http://localhost:8517/`:
  - PASS: `Data Actions`, compact `Detail`, `Macro Data`, macro signal cards, score chips rendered.
  - PASS: old full-width `Candle Symbol` row removed.
  - PASS: raw `<div>` / `<span>` leakage fixed.
  - PASS: mini chart cards show compact `60m`, `15m`, and `Age` chips with readable charts.
  - QA screenshots saved as generated artifacts: `futures-monitor-ui-v21-qa.png`, `futures-monitor-ui-v21-charts-qa.png`.

## 2026-06-02 V2.2 stacked 3x2 layout

- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py app/services/futures_market_monitoring.py finance/data/futures_market.py` - PASS.
- `git diff --check` - PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS.
- `uv run python -m unittest tests.test_service_contracts` - PASS, 234 tests.
- `uv run python - <<'PY' ... run_collect_futures_ohlcv(symbols=['GC=F','6J=F'], period='1d', interval='1m') ... PY` - PASS, 796 rows written for QA data coverage.
- Browser QA on `http://localhost:8517/` after Streamlit restart:
  - PASS: Macro Context renders above Live Futures Charts.
  - PASS: `Macro Evidence & Data` replaced separate `Macro Data`, `Macro validation detail`, and `Macro caveats` labels.
  - PASS: `Selected Detail` chart removed.
  - PASS: 3x2 grid includes `NQ=F`, `ZN=F`, `CL=F`, `6E=F`, `GC=F`, `6J=F`.
  - QA screenshots saved as generated artifacts: `futures-monitor-stack-v3x2-qa.png`, `futures-monitor-stack-v3x2-grid-qa.png`.

## 2026-06-02 V2.3 control cleanup

- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py finance/data/futures_market.py app/services/futures_market_monitoring.py` - PASS.
- `git diff --check` - PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` - PASS.
- `uv run python -m unittest tests.test_service_contracts` - PASS, 234 tests.
- Browser QA on `http://localhost:8517/`:
  - PASS: top controls show `Watch Group`, `Symbols`, `Window`, `Chart`, and `Data Actions`; `Focus` is no longer visible.
  - PASS: chart dropdown exposes `1m`, `5m`, `15m`, and `60m`; `1h` is no longer exposed.
  - PASS: command center shows `Pre-open Core · 6 selected`.
  - PASS: Live Futures Charts header shows `6 selected futures · 5m candles · 6H window`.
  - PASS: `Selected Detail` remains removed and the 3x2 chart grid remains below Macro Context.
  - QA screenshot saved as generated artifact: `futures-monitor-clean-controls-qa.png`.
