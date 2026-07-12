# Runs

## 2026-07-09

- `sed` read skill files: `finance-task-intake`, `finance-backtest-web-workflow`, `superpowers:brainstorming`.
- `sed` read finance docs in AGENTS read order.
- `rg --files` and `rg -n` inspected Final Review, Practical Validation REVIEW role, selected-route, and Portfolio Monitoring handoff code/tests.
- `git status --short` showed many untracked generated QA screenshots and local run history; these were not touched.
- `.venv/bin/python -m pytest ...` failed because pytest is not installed in `.venv`; switched to `unittest`.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_record_guide_records_non_select_judgment_without_monitoring_handoff tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_save_evaluation_uses_investability_packet_gate tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_decision_row_stores_non_select_judgment_without_monitoring_candidate` failed for expected old behavior.
- GREEN narrow: same three tests passed after implementation.
- GREEN related: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests` ran 82 tests and passed.
- `git diff --check` passed during mid-implementation hygiene check.
- `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review/page.py app/runtime/backtest/stores/portfolio_selection.py app/runtime/backtest/read_models/final_selected_portfolios.py` passed.
- Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.address 127.0.0.1 --server.port 8531 --server.headless true --server.runOnSave false --server.fileWatcherType none`, opened `/backtest`, selected `최종 검토 · Final Review`, switched `최종 판단 route` to `내용 부족 / 관찰 필요`, confirmed `Decision Save`, `Final Review 판단 저장`, `Decision Only`, and no Traceback / Exception. Screenshot emitted in Codex response; generated screenshot files were not staged.
- Full `tests.test_service_contracts` ran 732 tests and failed 1 unrelated existing contract: `OverviewAutomationContractTests.test_sentiment_react_summary_surface_prioritizes_state_and_freshness` expected `payload.summary.metrics.map` in the Sentiment React source. Final Review / Monitoring tests still passed.
