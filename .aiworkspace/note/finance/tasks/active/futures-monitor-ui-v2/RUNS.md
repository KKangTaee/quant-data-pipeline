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
