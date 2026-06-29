# Runs

Status: Completed
Last Verified: 2026-06-08

## Commands

- `uv run python -m unittest tests.test_backtest_etf_current_anchor`
  - Initial RED: failed because `app.services.backtest_etf_current_anchor` did not exist yet.
  - GREEN: passed after adding the read model.
- `uv run python -m unittest tests.test_backtest_etf_current_anchor tests.test_backtest_etf_evidence_expansion tests.test_backtest_risk_on_governance tests.test_backtest_strategy_bridge tests.test_backtest_strategy_evidence_inventory tests.test_reference_contextual_help`
  - Result: PASS, 26 tests.
- `uv run python -m py_compile app/services/backtest_etf_current_anchor.py app/web/backtest_analysis.py tests/test_backtest_etf_current_anchor.py`
  - Result: PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.
- `git diff --check`
  - Result: PASS.

## Browser QA

- URL: `http://localhost:8502/backtest`
- Evidence: `/tmp/backtest-4a-etf-current-anchor-workbench-qa.png`
- Result: PASS. Backtest Analysis shows `ETF Current Anchor Workbench` with latest run count, source count, ready count, evidence gap count, strategy readiness rows, detail expanders, and read-only storage / route boundary.
- Observed local artifact state: no matching GRS / Risk Parity / Dual Momentum latest run/source rows were loaded, so the panel correctly shows `RERUN_REQUIRED` for all three target strategies.
