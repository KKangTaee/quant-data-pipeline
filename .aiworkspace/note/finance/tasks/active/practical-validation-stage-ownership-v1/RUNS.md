# Runs

- 2026-07-09: Read superpowers using-superpowers, brainstorming, writing-plans, executing-plans, test-driven-development, verification-before-completion.
- 2026-07-09: Read finance task/backtest workflow/doc-sync skills and finance docs read order.
- 2026-07-09: Inspected Practical Validation module plan, workspace read model, Flow4 UI, Final Review evidence read model.
- 2026-07-09: RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_keeps_review_only_categories_visible_with_stage_role -v` failed because `final_review_reference_count` was 1.
- 2026-07-09: RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_flow4_uses_criteria_detail_board -v` failed because Flow4 filtered out REVIEW cards.
- 2026-07-09: GREEN: focused REVIEW role and Flow4 source contracts passed after read-model/UI updates.
- 2026-07-09: GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests -v` ran 99 tests OK.
- 2026-07-09: GREEN: `.venv/bin/python -m py_compile app/services/backtest_practical_validation_stage_roles.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/backtest_final_review/page.py`.
- 2026-07-09: GREEN: `git diff --check`.
- 2026-07-09: Browser QA: launched fresh Streamlit server on `http://localhost:8517`, ran Flow 2 replay, confirmed Flow 4 markers `카테고리별 검증 결과`, `데이터 보강 / 수집 실행`, `상세 근거 / 원자료` present and removed/old markers `단계별 검증 소유권`, `수집 대상 근거`, `Provider / Data 보강 액션`, `Provider 부족 근거` absent.
- 2026-07-09: Browser QA screenshot: `practical-validation-stage-ownership-v1-latest-data-action-board-qa.png`.
