# Runs

Commands and QA evidence for V1-V4 will be recorded here.

## V1

RED:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary
```

Expected failure confirmed because `_render_real_money_details` still called `_render_policy_signal_summary_panel(meta)`.

GREEN / QA:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_hold_candidates_as_conditional_review tests.test_service_contracts.BacktestRuntimeContractTests.test_candidate_review_draft_captures_handoff_readiness_snapshot tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_step1_receives_backtest_review_focus_queue
.venv/bin/python -m py_compile app/web/backtest_result_display.py tests/test_service_contracts.py
git diff --check
```

Result: passed. `edgar` deprecation warnings are unrelated dependency warnings.

## V2

RED:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_uses_single_integrated_action_surface
```

Expected failure confirmed because `_render_practical_validation_handoff_action_shell` did not exist yet.

GREEN / QA:

```bash
.venv/bin/python -m py_compile app/web/backtest_result_display.py tests/test_service_contracts.py
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_uses_single_integrated_action_surface tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_gate_allows_hold_candidates_as_conditional_review
git diff --check
```

Browser QA:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8513 --server.headless true --server.runOnSave false --server.fileWatcherType none
```

Checked `http://localhost:8513/backtest` with Equal Weight / Dividend ETFs. Handoff showed `Source 등록 액션`; Policy Signals showed `검증 기준 상세`.
