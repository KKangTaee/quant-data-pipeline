# Overview Market Intelligence Productionization Integration

## Expected Code Areas

- `finance/data/market_intelligence.py`
- `finance/data/db/schema.py`
- `app/jobs/ingestion_jobs.py`
- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/web/streamlit_app.py`
- `app/web/overview_dashboard_helpers.py`
- `tests/test_service_contracts.py`

## Expected Docs

- `.aiworkspace/note/finance/docs/data/`
- `.aiworkspace/note/finance/docs/architecture/`
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- `.aiworkspace/note/finance/WORK_PROGRESS.md`
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

## Integration Rules

- Overview render code must stay DB-only.
- Remote collection must run through ingestion jobs or scheduled automation.
- Do not mutate registries or saved portfolio JSONL.
- Service layer remains Streamlit-free.
- Browser smoke is required for visible Overview changes.

## Verification Gate

```bash
uv run python -m py_compile app/web/overview_dashboard.py app/web/streamlit_app.py app/jobs/ingestion_jobs.py finance/data/market_intelligence.py
uv run python -m unittest tests.test_service_contracts
uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```
