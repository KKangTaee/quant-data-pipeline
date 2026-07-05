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

## V3

RED:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_component_poc_is_isolated
```

Expected failure confirmed because `app/web/components/backtest_handoff_action/component.py` did not exist.

GREEN / QA:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_component_poc_is_isolated tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_uses_single_integrated_action_surface
.venv/bin/python -m py_compile app/web/components/__init__.py app/web/components/backtest_handoff_action/__init__.py app/web/components/backtest_handoff_action/component.py tests/test_service_contracts.py
git diff --check
node -e "const fs=require('fs'); const p=JSON.parse(fs.readFileSync('app/web/components/backtest_handoff_action/frontend/package.json','utf8')); if(!p.dependencies['streamlit-component-lib']) process.exit(1); console.log(p.name + ':' + p.version)"
```

Result: passed. The React POC is source-only and not wired into production.

## V4

RED:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_adoption_decision_is_documented
```

Expected failure confirmed because durable docs did not yet state the Handoff / Policy Signals responsibility split or the React POC adoption decision.

GREEN / QA:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_adoption_decision_is_documented tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_component_poc_is_isolated tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_uses_single_integrated_action_surface tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary
.venv/bin/python -m py_compile app/web/backtest_result_display.py app/web/components/backtest_handoff_action/component.py tests/test_service_contracts.py
git diff --check
```

Result: passed.

## 2026-07-05 correction

RED / environment note:

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k "handoff_uses_single_integrated_action_surface or handoff_react_component_is_production_action_card or handoff_react_adoption_decision"
python3 -m pytest tests/test_service_contracts.py -k "handoff_uses_single_integrated_action_surface or handoff_react_component_is_production_action_card or handoff_react_adoption_decision"
```

Result: local environment has no `pytest` module, so focused `unittest` methods were used for executable contract checks.

GREEN / QA:

```bash
npm install
npm run build
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_handoff_uses_single_integrated_action_surface tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_component_is_production_action_card tests.test_service_contracts.BacktestRuntimeContractTests.test_backtest_handoff_react_adoption_decision_is_documented
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests
.venv/bin/python -m py_compile app/web/backtest_result_display.py app/web/components/backtest_handoff_action/component.py tests/test_service_contracts.py
git diff --check
```

Browser QA:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8514 --server.headless true --server.runOnSave false --server.fileWatcherType none
```

Checked `http://localhost:8514/backtest` with Equal Weight / Dividend ETFs. The React iframe rendered `2차 실전성 검증 Handoff` and the `2차 검증으로 보내기` button inside the same Handoff card. Initial Browser QA exposed Vite absolute `/assets/...` paths; `vite.config.ts` now uses `base: "./"` and the rebuilt component loads relative assets correctly.
