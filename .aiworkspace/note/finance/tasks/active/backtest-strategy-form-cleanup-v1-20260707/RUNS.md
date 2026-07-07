# Runs

Commands and QA evidence will be appended per task.

## 2026-07-07 1차 Strategy Detail Panel Removal

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_single_strategy_workspace_does_not_render_strategy_detail_panel -v` failed because `app/web/backtest_single_strategy.py` still imported and rendered the panel.
- GREEN: focused tests passed for `test_single_strategy_workspace_does_not_render_strategy_detail_panel` and `test_price_freshness_preflight_react_component_is_ui_only`.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_single_strategy.py app/web/backtest_single_forms/__init__.py app/web/backtest_common.py` completed successfully.
- Reference scan: active app/docs references to `backtest_strategy_detail` / `Strategy Detail` are removed except the negative assertion in the test.

## 2026-07-07 2차 Strict Preset Helper Cleanup

- RED: strict preset helper tests failed with missing `display_items`, `preset_tone`, and `preset_role` fields.
- GREEN: focused strict preset helper tests passed after adding compact display fields.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py` completed successfully.
- Diff check: `git diff --check` completed successfully.

## 2026-07-07 3차 Strict Factor Single Strategy Forms

- RED: `test_strict_factor_single_forms_keep_guidance_inside_form_surface` failed because strict forms still used broad guide / long data requirements and had no compact data readiness helper.
- GREEN: focused tests passed for strict form surface and Price Freshness Preflight component contracts.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_single_forms/strict_factor.py app/web/backtest_common.py` completed successfully.
- Browser QA: Selenium confirmed the overbuilt `Strategy Detail` panel is absent, Quality Strict Annual shows `데이터 준비 기준` / compact preset basis / Price Freshness, and Value Strict Quarterly shows data readiness plus Statement Shadow Coverage Preview. Price Freshness rendered inside the component iframe with no component asset errors.
- Screenshots: `backtest-select-quality-debug.png`, `backtest-value-quarterly-form-cleanup-v1-qa.png`, and `backtest-value-quarterly-form-cleanup-v1-scrolled-qa.png` generated locally and not intended for commit.

## 2026-07-07 4차 ETF-Like Single Strategy Forms

- RED/GREEN: `test_etf_like_single_forms_stay_form_first_without_runtime_wrapper_copy` failed on legacy `runtime wrapper` copy, then passed after keeping layouts intact and replacing only visible strategy descriptions.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_single_forms/equal_weight.py app/web/backtest_single_forms/gtaa.py app/web/backtest_single_forms/global_relative_strength.py app/web/backtest_single_forms/risk_parity.py app/web/backtest_single_forms/dual_momentum.py` completed successfully.
- Diff check: `git diff --check` completed successfully.
- Browser QA: Selenium opened `/backtest`, confirmed Equal Weight and GTAA show form-first controls, no `Strategy Detail`, visible `Advanced Inputs`, and the expected run buttons.
- Screenshot: `backtest-etf-like-form-cleanup-v1-qa.png` generated locally and not intended for commit.

## 2026-07-07 5차 Portfolio Mix Builder Impact / Docs Closeout

- Focused contract: `test_portfolio_mix_builder_remains_streamlit_owned_with_strict_preset_copy` passed and confirms compare mode does not depend on the removed Strategy Detail panel.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_compare/page.py` completed successfully.
- Browser QA: Selenium opened `/backtest`, switched to `Portfolio Mix Builder`, confirmed no `Strategy Detail`, then added `Quality` to the strategy multiselect and confirmed `Quality Snapshot (Strict Annual)` plus compact `현재 기준 / 업데이트 방법` preset copy rendered.
- Screenshots: `backtest-portfolio-mix-form-cleanup-v1-qa.png` and `backtest-portfolio-mix-strict-form-cleanup-v1-qa.png` generated locally and not intended for commit.
- Docs sync: updated docs index, roadmap, project map, script structure map, Backtest UI flow, root progress log, and question / analysis log.
