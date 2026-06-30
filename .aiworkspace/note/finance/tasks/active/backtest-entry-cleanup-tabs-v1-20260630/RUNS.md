# Runs

## 2026-06-30

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_uses_compact_korean_english_workflow_tabs tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_removes_unused_guide_snapshot_and_reference_panels
```

- Result: RED. Existing code still used `segmented_control` / `st.radio` and still contained `Backtest 사용 안내`.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_uses_compact_korean_english_workflow_tabs tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_removes_unused_guide_snapshot_and_reference_panels
```

- Result: GREEN, 2 tests.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests
```

- Result: GREEN, 16 tests.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestPresetCatalogContractTests tests.test_service_contracts.BacktestRuntimeContractTests tests.test_service_contracts.BacktestRealismAuditContractTests
```

- Result: GREEN, 25 tests.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_uses_compact_korean_english_workflow_tabs tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_page_removes_unused_guide_snapshot_and_reference_panels tests.test_service_contracts.BoundaryContractHardeningTests tests.test_service_contracts.BacktestPresetCatalogContractTests tests.test_service_contracts.BacktestRuntimeContractTests tests.test_service_contracts.BacktestRealismAuditContractTests
```

- Result: GREEN, 43 tests.

```bash
.venv/bin/python -m py_compile app/web/backtest_page.py app/web/backtest_analysis.py app/web/backtest_common.py app/web/backtest_single_strategy.py app/web/backtest_single_forms.py app/web/backtest_compare.py tests/test_service_contracts.py
git diff --check
```

- Result: GREEN.

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8528 --server.headless true --server.runOnSave false --server.fileWatcherType none
```

- Result: Browser QA passed at `http://127.0.0.1:8528/backtest`.
- Checked labels: `후보 분석 · Backtest Analysis`, `실전 검증 · Practical Validation`, `최종 검토 · Final Review`.
- Checked removed text: `Backtest 사용 안내`, `Strategy Capability Snapshot`, `전략 개발 참고`.
- Checked active tab color / underline: `rgb(255, 75, 75)`.
- Checked native Streamlit sidebar text: absent.
