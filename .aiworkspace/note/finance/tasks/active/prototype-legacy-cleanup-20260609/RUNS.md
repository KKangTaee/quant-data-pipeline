# Prototype Legacy Cleanup / Removal Runs

## 2026-06-09

- `sed` reads: core docs, flow docs, architecture docs, product research recommendation / feature candidates.
- `git status --short`: dirty tree contains pre-existing saved JSONL, `.DS_Store`, run history, and screenshot artifacts.
- `rg` legacy inventory: Candidate Review / Portfolio Proposal remain in route helpers and Backtest page dispatch; Overview Candidate Ops still reads current/pre-live/proposal registries.
- Focused route / Overview / archive handoff tests were added in `tests/test_service_contracts.py` and first run red against the legacy implementation.
- Focused tests then passed after code changes:
  - `.venv/bin/python -m unittest tests.test_service_contracts.PrototypeLegacyCleanupTests -v`
  - `.venv/bin/python -m unittest tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_links_selected_final_review_rows -v`
- Durable docs search was rerun after sync. Remaining `Selected Portfolio Dashboard` references are intentional legacy file/helper aliases; Candidate Review / Portfolio Proposal references are marked legacy / archive compatibility instead of current primary workflow.
- Final verification passed:
  - `.venv/bin/python -m unittest tests.test_service_contracts.PrototypeLegacyCleanupTests tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_links_selected_final_review_rows tests.test_service_contracts.DecisionDossierContractTests.test_decision_dossier_is_read_only_markdown_export -v`
  - `.venv/bin/python -m py_compile app/web/backtest_workflow_routes.py app/web/pages/backtest.py app/web/overview_dashboard.py app/web/backtest_history.py app/web/backtest_candidate_library.py app/web/backtest_final_review.py app/web/final_selected_portfolio_dashboard.py app/runtime/final_selected_portfolios.py app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_selected_route_preflight.py app/services/reference_contextual_help.py app/web/reference_guides.py app/services/reference_guides_catalog.py app/web/streamlit_app.py app/web/ops_review.py app/web/ingestion_console.py app/web/backtest_practical_validation.py app/web/backtest_single_strategy.py app/web/backtest_final_review_helpers.py`
  - `git diff --check`
- Browser QA:
  - Started Streamlit with `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8501 --server.headless true`.
  - `http://localhost:8501/backtest` showed Backtest Analysis / Practical Validation / Final Review and did not show Candidate Review / Portfolio Proposal / Pre-Live.
  - QA screenshot: `prototype-legacy-cleanup-qa-20260609.png`.
  - Streamlit emitted an unrelated `use_container_width` deprecation warning on shutdown.

Detailed command outputs stay in chat/tool logs; this file records only durable outcomes.

## 2026-06-10

- 5C focused tests were added first and initially ran red against the old implementation because current modules still imported legacy Candidate/Proposal helpers and the deleted-module contract was not satisfied.
- Current Practical Validation handoff extraction then passed focused tests:
  - `.venv/bin/python -m unittest tests.test_service_contracts.PrototypeLegacyCleanupTests -v`
- Final verification passed:
  - `.venv/bin/python -m unittest tests.test_service_contracts.PrototypeLegacyCleanupTests tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_links_selected_final_review_rows tests.test_service_contracts.DecisionDossierContractTests.test_decision_dossier_is_read_only_markdown_export -v`
  - `.venv/bin/python -m py_compile app/services/backtest_practical_validation_source.py app/web/backtest_practical_validation_handoff.py app/web/backtest_common.py app/web/backtest_result_display.py app/web/backtest_compare.py app/web/backtest_history.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py app/web/overview_dashboard_helpers.py app/web/overview_dashboard.py app/web/pages/backtest.py app/web/backtest_candidate_library.py app/runtime/candidate_registry.py app/runtime/portfolio_proposal.py app/runtime/paper_portfolio_ledger.py app/runtime/final_selected_portfolios.py`
  - `git diff --check`
- Browser QA:
  - Started Streamlit with `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8501 --server.headless true`.
  - `http://localhost:8501/backtest` showed `Backtest Analysis`, `Practical Validation`, and `Final Review`; it did not show `Candidate Review`, `Portfolio Proposal`, or `Pre-Live`.
  - QA screenshot: `prototype-legacy-cleanup-5c-qa-20260610.png`.
  - Test output included unrelated `edgar` deprecation warnings; Streamlit shutdown emitted the existing `use_container_width` deprecation warning.
