# Runs

Commands and QA evidence will be appended per task.

## 2026-07-07 0차 Price Freshness Preflight

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_price_freshness_preflight_react_component_is_ui_only -v` failed because `base: "./"` was missing from the preflight Vite config.
- Build: `npm run build` in `app/web/components/backtest_price_freshness_preflight/frontend` completed successfully.
- GREEN: the same focused unittest passed after rebuild.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_strategy.py app/web/backtest_single_forms/*.py app/web/components/backtest_price_freshness_preflight/component.py` completed successfully.
- Browser QA: Selenium opened `/backtest`, selected `Quality`, inspected the component iframe, and confirmed `Price Freshness Preflight` text rendered with `./assets/...` paths. Previous component asset MIME error was not present.
- Screenshot: `backtest-price-freshness-preflight-fixed-qa.png` generated locally and not intended for commit.

## 2026-07-07 1차 Strategy Detail Read Model

- RED: focused read-model tests failed with `ModuleNotFoundError` because `app/services/backtest_strategy_detail.py` did not exist yet.
- GREEN: focused read-model tests passed after adding `build_backtest_strategy_detail_model`.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_strategy_detail.py` completed successfully.
- Diff check: `git diff --check -- app/services/backtest_strategy_detail.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/backtest-strategy-detail-react-v1-20260707` completed successfully.

## 2026-07-07 2차 Strategy Detail React Panel

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_backtest_strategy_detail_panel_react_component_is_ui_only -v` failed because `app/web/components/backtest_strategy_detail_panel/component.py` did not exist yet.
- Build setup: `npm install` in `app/web/components/backtest_strategy_detail_panel/frontend` completed with npm audit warnings already typical of this Vite dependency family; no dependency upgrade was applied.
- Build: `npm run build` in `app/web/components/backtest_strategy_detail_panel/frontend` completed successfully.
- GREEN: component contract test passed after wrapper/frontend/build/wiring were added.
- RED/GREEN polish: strict factor run-action label tests first failed on generated labels, then passed after explicit button labels were added to `app/services/backtest_strategy_detail.py`.
- Focused verification: 7 relevant `BacktestCandidateAnalysisHardeningTests` passed.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_strategy_detail.py app/web/backtest_single_strategy.py app/web/backtest_single_forms/__init__.py app/web/components/backtest_strategy_detail_panel/component.py` completed successfully.
- Browser QA: Selenium confirmed `Strategy Detail` panel renders for Equal Weight and Quality Strict Annual, Quality includes `Run Strict Annual Quality Backtest`, and Price Freshness Preflight still renders. No component asset MIME errors were logged.
- Screenshot: `backtest-strategy-detail-panel-qa.png` generated locally and not intended for commit.
