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
