# Practical Validation Diagnostics Split Runs

Status: Active
Created: 2026-05-27

## Initial Commands

```bash
rg -n "^(def|class) " app/services/backtest_practical_validation_diagnostics.py
rg -n "build_validation_profile|build_selection_source_from_candidate_draft|build_selection_source_from_saved_mix_prefill|build_selection_source_from_weighted_mix_prefill|source_components_dataframe|compact_curve_snapshot_from_bundle|compact_benchmark_curve_snapshot_from_bundle" app tests .aiworkspace/note/finance/docs -g '*.py' -g '*.md'
rg -n "json\\.|\\bjson\\b|_slug\\(|_metric_snapshot_from_result\\(|VALIDATION_PROFILE_OPTIONS|VALIDATION_PROFILE_QUESTIONS|VALIDATION_PROFILE_DOMAIN_WEIGHTS|PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION|uuid4\\(|datetime\\.now" app/services/backtest_practical_validation_diagnostics.py
```

## Initial Result

- Source/profile builder functions are clustered near the top of diagnostics.
- `json` remains needed later for stress/overfit rows and cannot be removed.
- `uuid4` / `_slug` / `_now_text` are still needed by final validation id generation.

## 7-01 Verification Commands

```bash
.venv/bin/python -m py_compile app/services/backtest_practical_validation_source.py app/services/backtest_practical_validation_diagnostics.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python -m unittest tests.test_service_contracts
git diff --check
```

## 7-01 Verification Results

- Python compile: PASS.
- Boundary lint: PASS, hard violations none, advisories none.
- Service contract tests: PASS, 17 tests.
- Diff check: PASS.
- Browser QA: not applicable because `7-01` changes service helper ownership/import paths only, with no visible Streamlit flow or displayed data shape change.

## 7-02 Analysis Commands

```bash
rg -n "compact_curve_snapshot_from_bundle|compact_benchmark_curve_snapshot_from_bundle|_normalize_result_curve|_summary_metrics_from_curve|_window_perturbation_rows|_aligned_monthly_returns|_format_percent|_parse_date|_price_proxy_curve|_combine_component_curves|_build_curve_context" app tests .aiworkspace/note/finance -g '*.py' -g '*.md'
rg -n "np\\." app/services/backtest_practical_validation_diagnostics.py
rg -n "load_price_history|portfolio_performance_summary|_curve_records_from_df" app/services/backtest_practical_validation_diagnostics.py
wc -l app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_curve_context.py
```

## 7-02 Analysis Result

- Shared curve helpers could move without changing diagnostics-specific component interpretation.
- `_build_curve_context` remains in diagnostics because it still depends on component title / weight / ticker interpretation helpers.
- Diagnostics line count is now 2258, and the new curve context helper is 306 lines.

## 7-02 Verification Commands

```bash
.venv/bin/python -m py_compile app/services/backtest_practical_validation_curve_context.py app/services/backtest_practical_validation_diagnostics.py app/web/backtest_candidate_review_helpers.py app/web/backtest_compare.py tests/test_service_contracts.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python -m unittest tests.test_service_contracts
git diff --check
```

## 7-02 Verification Results

- Python compile: PASS.
- Boundary lint: PASS, hard violations none, advisories none.
- Service contract tests: PASS, 17 tests.
- Diff check: PASS.
- Browser QA: not applicable because `7-02` changes service helper ownership/import paths only, with no visible Streamlit flow or displayed data shape change.
