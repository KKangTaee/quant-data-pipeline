# Runs

Status: Completed
Last Verified: 2026-06-07

## RED

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_delegates_read_only_diagnostics_to_service_facade \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_diagnostics_service_owns_public_entrypoints
```

Result: expected failure before implementation.

- `app.services.ingestion_diagnostics` module did not exist.
- `app/web/ingestion_console.py` still imported `app.jobs.diagnostics` directly.

## GREEN / Focused Verification

```bash
.venv/bin/python -m py_compile app/services/ingestion_diagnostics.py app/web/ingestion_console.py tests/test_service_contracts.py
```

Result: passed.

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_delegates_read_only_diagnostics_to_service_facade \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_diagnostics_service_owns_public_entrypoints
```

Result: passed, 2 tests.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests
```

Result: passed, 11 tests.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result: passed. Hard violations: none. Advisories: none.

## Closeout Verification

```bash
.venv/bin/python -m py_compile app/services/ingestion_diagnostics.py app/web/ingestion_console.py tests/test_service_contracts.py
```

Result: passed.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 285 tests.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result: passed. Hard violations: none. Advisories: none.

```bash
curl -fsS http://localhost:8501/_stcore/health
```

Result: `ok`.

## Browser QA

- In-app browser DOM QA loaded `http://localhost:8501/ingestion`, opened `수동 복구 / 진단`, and confirmed these text signals: `Ingestion`, `가격 stale 원인 진단`, `재무제표 coverage 원인 진단`, `재무제표 PIT inspection`.
- In-app screenshot capture timed out on `Page.captureScreenshot`; fallback Playwright QA navigated through the top navigation to `Workspace > Ingestion`, opened the same diagnostics tab, and confirmed the same text signals.
- Screenshot artifacts created for QA only and not staged: `ingestion-7b-diagnostics-qa.png`, `ingestion-7b-diagnostics-cards-qa.png`, `ingestion-7b-root-fallback.png`.
