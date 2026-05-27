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
