# Futures Macro Evidence / Original Data UX Runs

## 2026-07-06

- Phase 1 RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_workbench_payload_keeps_python_action_boundary tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_component_scaffold_keeps_streamlit_fallback` failed as expected because payload title was `근거 해석` and the lower expander still used `근거 해석 / 원본 데이터`.
- Phase 1 GREEN: same focused unittest passed after splitting React `현재 근거` from lower `계산 근거 / 원본 표`.
- Phase 1 QA: `.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py` passed.
- Phase 1 QA: `git diff --check -- app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/overview-futures-macro-evidence-original-data-ux-20260706` passed.
