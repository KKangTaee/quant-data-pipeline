# Runs

No commands recorded yet.
# Runs

## 2026-05-31

```bash
.venv/bin/python -m py_compile app/web/backtest_final_review.py app/web/backtest_final_review_components.py
```

Result: passed.

```bash
rg -n "render_artifact_pipeline|_render_policy_row_list" app/web/backtest_final_review.py app/web/backtest_final_review_components.py
```

Result: no matches after removing the unused import / helper.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 207 tests.

```bash
git diff --check
```

Result: passed.

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8504 --server.headless true
```

Result: Browser QA passed for `http://127.0.0.1:8504/backtest` -> `Final Review`.
Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/final-review-commercial-ux-v1-qa.png`.

Note: Streamlit still emits a repo-wide `use_container_width` deprecation warning from existing Backtest code. This task did not introduce new `use_container_width` usage.

```bash
.venv/bin/python -m py_compile app/web/backtest_final_review.py app/web/backtest_final_review_components.py
git diff --check
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed after the candidate-scoped `Source` / `Decision ID` widget key fix. Service contract suite passed with 207 tests.

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8504 --server.headless true
```

Result: Browser QA passed for `http://127.0.0.1:8504/backtest` -> `Final Review`; advanced Decision ID area rendered with the current source ID and generated source-scoped decision ID.
Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/final-review-widget-key-fix-qa.png`.

Note: Local fixture had one eligible Final Review candidate, so direct multi-candidate switching was not available in Browser QA. The code path now scopes the affected widget keys by `source_slug`.

```bash
.venv/bin/python -m py_compile app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py app/services/backtest_evidence_read_model.py
.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests
```

Result: passed after changing official Final Review save to selection-only. The first attempted targeted unittest used an outdated class name and failed before running tests; rerunning with `FinalReviewEvidenceReadModelContractTests` passed 30 tests.

```bash
.venv/bin/python -m py_compile app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_modules.py app/runtime/final_selected_portfolios.py app/web/final_selected_portfolio_dashboard.py app/web/backtest_practical_validation.py app/web/backtest_compare.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py app/web/pages/backtest.py app/web/reference_guides.py
.venv/bin/python -m unittest tests.test_service_contracts
git diff --check
```

Result: final verification passed. Service contract suite passed with 207 tests.

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8504 --server.headless true
```

Result: Browser QA passed for `http://127.0.0.1:8504/backtest` -> `Final Review`; the page showed selection-only official save copy and the blocked local fixture kept `최종 후보로 선정` disabled.
Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/final-review-selection-only-save-qa.png`.

Note: Streamlit still emits the existing repo-wide `use_container_width` deprecation warning. Browser console also reports Streamlit health / host-config 404s around route reload; the page rendered successfully.
