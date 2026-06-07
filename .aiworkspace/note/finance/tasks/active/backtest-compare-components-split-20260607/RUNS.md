# Runs

Status: Completed
Last Verified: 2026-06-07

## RED

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_compare_delegates_visual_shell_to_component_module \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_compare_components_module_owns_visual_entrypoints
```

Result: expected failure before implementation.

- `app.web.backtest_compare_components` did not exist.
- `app/web/backtest_compare.py` still owned the visual shell helper functions directly.

## GREEN / Focused Verification

```bash
.venv/bin/python -m py_compile app/web/backtest_compare.py app/web/backtest_compare_components.py tests/test_service_contracts.py
```

Result: passed.

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_compare_delegates_visual_shell_to_component_module \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_compare_components_module_owns_visual_entrypoints
```

Result: passed, 2 tests.

## Closeout Verification

```bash
.venv/bin/python -m py_compile app/web/backtest_compare.py app/web/backtest_compare_components.py tests/test_service_contracts.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 287 tests.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result: passed.

```bash
git diff --check
curl -fsS http://localhost:8501/_stcore/health
```

Result: passed. Streamlit health returned `ok`.

## Browser QA

- Verified `http://localhost:8501/backtest` in Portfolio Mix Builder mode.
- Confirmed the screen renders the Portfolio Mix Builder title, Component Run card, Strategy Weight inputs, Practical Validation label, and 4-step builder strip.
- In-app Browser screenshot capture timed out during CDP capture, so the QA image was captured with the Browser/Playwright fallback.
- Screenshot artifact: `/Users/taeho/Project/quant-data-pipeline/backtest-compare-9a-qa.png`
- Screenshot artifact is generated output and should not be staged unless explicitly requested.
