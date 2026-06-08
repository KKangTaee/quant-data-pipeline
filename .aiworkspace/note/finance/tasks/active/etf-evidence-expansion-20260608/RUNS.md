# Runs

Status: Completed
Last Verified: 2026-06-08

## Commands

- `uv run python -m unittest tests.test_backtest_etf_evidence_expansion`
  - Initial RED: failed because `app.services.backtest_etf_evidence_expansion` did not exist yet.
  - GREEN: passed after adding the read model.
- `uv run python -m unittest tests.test_backtest_etf_evidence_expansion tests.test_backtest_risk_on_governance tests.test_backtest_strategy_bridge tests.test_backtest_strategy_evidence_inventory tests.test_reference_contextual_help`
  - Result: PASS, 22 tests.
- `uv run python -m py_compile app/services/backtest_etf_evidence_expansion.py app/web/backtest_analysis.py tests/test_backtest_etf_evidence_expansion.py`
  - Result: PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS, hard violations none, advisories none.
- `git diff --check`
  - Result: PASS.

## Browser QA

- URL: `http://localhost:8502/backtest`
- Evidence: `/tmp/backtest-3d-etf-evidence-expansion-qa.png`
- Result: PASS. Backtest Analysis shows `ETF Evidence Expansion` with target count, baseline reference count, disabled candidate writes / reruns, ETF evidence target rows, strategy detail expanders, and next workflow rows.
